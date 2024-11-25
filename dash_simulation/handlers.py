import asyncio
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

    async def update_streams(self, ddf):
        promises = [handler(stream, ddf) for handler, stream in self.out_stream_handlers]
        for p in promises:
            await p

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
            asyncio.run(self.update_streams(ddf))
            logger.success(f"{len(ddf)} datapoints sent to plot stream!")
        else:
            logger.info(f"Skipping {f} (already loaded)")


async def update_stream(stream, obj):
    logger.info(f"Streaming {obj} to {stream}...")
    stream.object = obj
    logger.success(f"{stream} updated!")


class TemperaturePlotHandler:
    def __init__(self, mt):
        self.mt = mt

    async def __call__(self, streams, ddf):
        logger.info("Updating tempreature plots.")
        local_mt = PatchedComposite(self.mt.client)
        local_mt.loader.data = ddf
        logger.info("Updating most recent temperature plots.")
        local_scatter, local_dist = self.plots_from_mt(local_mt)
        local_scatter = local_scatter.opts(title="Most Recent Layer Temperature Map")
        local_dist = local_dist.opts(title="Most Recent Layer Temperature Distribution")
        logger.info("Updating overall temperature plots.")
        overall_scatter, overall_dist = self.plots_from_mt(self.mt)
        overall_scatter = overall_scatter.opts(title="Overall Temperature Map")
        overall_dist = overall_dist.opts(title="Overall Temperature Distribution")
        scatters = (overall_scatter + local_scatter).opts(shared_axes=True)
        dists = (overall_dist + local_dist).opts(height=300, shared_axes=True)
        scatter_stream, dist_stream = streams

        p1 = asyncio.create_task(update_stream(scatter_stream, scatters))
        p2 = asyncio.create_task(update_stream(dist_stream, dists))
        await p1
        await p2

    def plots_from_mt(self, mt):
        scatter = mt.scatter2d()
        dist = hv.Distribution(mt.loader.data, kdims=["t"])
        return scatter, dist


class TableHandler:
    def __init__(self, client):
        self.client = client

    async def __call__(self, stream, ddf):
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
        await update_stream(stream, pd.concat([stream.object, df]).reset_index(drop=True))
