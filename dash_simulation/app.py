import atexit
import holoviews as hv
import holoviews.operation.datashader as hd
from loguru import logger
from mtpy import MeltpoolTomography
from mtpy.proc.statistics import Statistics

from mtpy.vis.vis2d.plotter import Plotter
import pandas as pd
import panel as pn
import time
from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer
import sys

from dash_simulation.patched_loader import PatchedAconityLoader


logger.remove()
logger.add(sys.stderr, colorize=True)
atexit.register(lambda: logger.warning("Closing python interpreter"))


hv.extension("plotly")


class PatchedComposite(MeltpoolTomography):
    def __init__(self, client=None):
        self.loader = PatchedAconityLoader(client)
        self.plotter = Plotter(self.loader)
        self.processor = Statistics(self.loader)


class LayerHandler(FileSystemEventHandler):
    def __init__(self, loader, *args, plot_handlers=None, out_streams=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.cached_files = set()
        self.loader = loader
        self.out_stream_handlers = (
            list(zip(plot_handlers, out_streams))
            if (plot_handlers is not None) and (out_streams is not None)
            else []
        )
        self.prev_len = 0

    def add_plot_stream(self, plot_handler, stream):
        self.out_stream_handlers.append((plot_handler, stream))
        logger.warning(
            f"Event output stream {stream} added with handler {plot_handler}"
        )

    def on_closed(self, event: FileSystemEvent) -> None:
        logger.info(event)
        if (f := event.src_path) not in self.cached_files:
            self.cached_files.add(f)
            logger.info(f"Reading {f}")
            ddf = self.loader.stream_layer(f)
            new_len = self.loader.data.shape[0].compute()
            logger.success(f"File {f} loaded! Current length: {new_len}")
            if self.out_stream_handlers is None:
                logger.warning("No output streams found!")
                return
            for handler, stream in self.out_stream_handlers:
                handler(stream, ddf)
            logger.success(f"{len(ddf)} datapoints sent to plot stream!")
        else:
            logger.info(f"Skipping {f} (already loaded)")


class IncrementalScatterHandler:
    def __init__(self, client):
        self.layer_rasters = []
        self.client = client

    def __call__(self, stream, ddf):
        mt = PatchedComposite(self.client)
        mt.loader.data = ddf
        self.layer_rasters.append(mt.scatter2d())
        opacity = 1 / len(self.layer_rasters)
        raster_iterator = iter(self.layer_rasters)
        overlay = next(raster_iterator).opts(alpha=opacity)
        for r in raster_iterator:
            overlay *= r.opts(alpha=opacity)
        stream.object = hd.dynspread(overlay)


def app():
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
    scatter_stream_handler = IncrementalScatterHandler(mt.client)
    dummy_chunk = pd.DataFrame.from_dict({"x": [], "y": [], "z": [], "t": []})
    dummy_raster = hd.dynspread(hd.rasterize(hv.Points(dummy_chunk)))
    scatter_pane = pn.pane.HoloViews(dummy_raster)
    event_handler.add_plot_stream(scatter_stream_handler, scatter_pane)
    return pn.template.MaterialTemplate(
        site="Panel",
        title="Live PBF Dashboard",
        main=[scatter_pane],
    )


if __name__.startswith("bokeh_app"):
    app().servable()
