import holoviews as hv
from loguru import logger
import pandas as pd
from watchdog.events import FileSystemEvent, FileSystemEventHandler

from dash_simulation.patched_composite import PatchedComposite


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
        logger.warning(f"Event output stream {stream} added with handler {plot_handler}")

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


class TemperaturePlotHandler:
    def __init__(self, mt):
        self.mt = mt

    def __call__(self, stream, ddf):
        logger.info("Updating tempreature plots.")
        local_mt = PatchedComposite(self.mt.client)
        local_mt.loader.data = ddf
        logger.info("Updating most recent temperature plots.")
        local_scatter, local_dist = self.plots_from_mt(local_mt)
        local_scatter = local_scatter.apply.opts(
            title="Most Recent Layer Temperature Map", xlim=(30, 140), ylim=(-150, -40)
        )
        local_dist = local_dist.apply.opts(
            title="Most Recent Layer Temperature Distribution", height=300
        )
        logger.info("Updating overall temperature plots.")
        overall_scatter, overall_dist = self.plots_from_mt(self.mt)
        overall_scatter = overall_scatter.apply.opts(
            title="Overall Temperature Map", xlim=(30, 140), ylim=(-150, -40)
        )
        overall_dist = overall_dist.apply.opts(title="Overall Temperature Distribution", height=300)
        logger.info("Streaming to dashboard.")
        stream.object = (local_scatter + overall_scatter + local_dist + overall_dist).cols(2)

    def plots_from_mt(self, mt):
        scatter = mt.scatter2d()
        dist = hv.Distribution(mt.loader.data, kdims=["t"])
        return scatter, dist


class TableHandler:
    def __init__(self, client):
        self.client = client

    def __call__(self, stream, ddf):
        logger.info("Calculating layer statistics...")
        mt = PatchedComposite(self.client)
        mt.loader.data = ddf
        stats = mt.calculate_stats(groupby="z")
        df = pd.DataFrame()
        for k, v in stats.items():
            df[k] = v["t"]
        df = df.reset_index().rename(
            {
                "z": "Z (mm)",
                "min": "Min",
                "max": "Max",
                "mean": "Mean",
                "std": "Std Dev",
                "stderr": "Std Err",
                "ci_error": "CI Err",
                "ci_min": "CI Min",
                "ci_max": "CI Max",
            },
            axis=1,
        )
        logger.info("Updating Table")
        stream.object = pd.concat([stream.object, df]).reset_index(drop=True)
