import atexit
import dask
import holoviews as hv
from loguru import logger
from mtpy import MeltpoolTomography
from mtpy.proc.statistics import Statistics
import pandas as pd
import panel as pn
import time
from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer
import sys

from dash_simulation.patched_loader import PatchedAconityLoader
from dash_simulation.patched_plotter import PatchedPlotter


logger.remove()
logger.add(sys.stderr, colorize=True)
atexit.register(lambda: logger.warning("Closing python interpreter"))


class PatchedComposite(MeltpoolTomography):
    def __init__(self):
        self.loader = PatchedAconityLoader()
        self.plotter = PatchedPlotter(self.loader)
        self.processor = Statistics(self.loader)


class LayerHandler(FileSystemEventHandler):
    def __init__(self, loader, *args, stream=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.cached_files = set()
        self.loader = loader
        self.stream = stream
        self.prev_len = 0

    def change_stream(self, stream):
        self.stream = stream
        self.prev_len = 0
        logger.warning(f"Event output stream changed to {self.stream}")

    def on_closed(self, event: FileSystemEvent) -> None:
        logger.info(event)
        if (f := event.src_path) not in self.cached_files:
            self.cached_files.add(f)
            logger.info(f"Reading {f}")
            self.loader.read_layer(f)
            new_len = self.loader.data.shape[0].compute()
            logger.success(f"File {f} loaded! Current length: {new_len}")
            if self.stream is None:
                logger.warning("No data stream found!")
                return
            # self.stream.send(self.loader.data.iloc[self.prev_len :].compute())
            pd.concat(
                dask.compute(
                    *(
                        self.loader.data[c][self.prev_len :]
                        for c in self.loader.data.columns
                    )
                ),
                axis=1,
            )
            logger.success(f"New data {self.prev_len}:{new_len} sent to plot stream!")
            self.prev_len = new_len
        else:
            logger.info(f"Skipping {f} (already loaded)")


def main():
    logger.info("Initialising application...")
    mt = PatchedComposite()
    event_handler = LayerHandler(mt.loader)
    observer = Observer()
    observer.schedule(event_handler, "./layers/", recursive=False)
    observer.start()
    atexit.register(observer.stop)
    atexit.register(observer.join)
    logger.success("Watcher ready!")
    while mt.loader.data is None:
        time.sleep(1)
    dummy_data = pd.DataFrame.from_dict({"x": [], "y": [], "z": [], "t": []})
    data_stream = hv.streams.Buffer(dummy_data)
    event_handler.change_stream(data_stream)
    plot = mt.scatter2d(stream=data_stream)
    component = pn.panel(plot)
    pn.serve(component, title="Streaming PBF dashboard", show=True)


if __name__ == "__main__":
    main()
