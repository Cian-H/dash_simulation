import holoviews.operation.datashader as hd
from loguru import logger
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


class FakePane:
    def __init__(self, obj):
        self.object = obj


class IncrementalFlattenedTempMapHandler:
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
        logger.info("Updating Flattened Temperature Map")
        stream.object = hd.dynspread(overlay).opts(title="Flattened Temperature Map")


class MostRecentTempMapHandler:
    def __init__(self, incflathandler: IncrementalFlattenedTempMapHandler):
        self.incflathandler = incflathandler

    def __call__(self, stream, *_):
        logger.info("Updating Most Recent Temperature Map")
        # No need to re-render, just grab the plot from the flattening object
        stream.object = self.incflathandler.layer_rasters[-1].opts(
            title="Most Recent Temperature Map"
        )


class CombinedTempMapHandler:
    def __init__(self, client):
        self.flattened_handler = IncrementalFlattenedTempMapHandler(client)
        self.mostrecent_handler = MostRecentTempMapHandler(self.flattened_handler)

    def __call__(self, stream, ddf):
        flattened_stream = FakePane(None)
        mostrecent_stream = FakePane(None)
        self.flattened_handler(flattened_stream, ddf)
        self.mostrecent_handler(mostrecent_stream, ddf)
        stream.object = flattened_stream.object + mostrecent_stream.object
