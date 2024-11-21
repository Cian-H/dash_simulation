import atexit
from loguru import logger
import panel as pn
import time
from watchdog.observers import Observer
import sys

from dash_simulation.dummy_plots import dummy_flattempmap, dummy_recenttempmap
from dash_simulation.handlers import (
    IncrementalFlattenedTempMapHandler,
    LayerHandler,
    MostRecentTempMapHandler,
)
from dash_simulation.patched_composite import PatchedComposite


logger.remove()
logger.add(sys.stderr, colorize=True)
atexit.register(lambda: logger.warning("Closing python interpreter"))


def app():
    # Create observer and register hooks for handling/cleanup
    logger.info("Initialising application...")
    mt = PatchedComposite()
    event_handler = LayerHandler(mt.loader)
    observer = Observer()
    observer.schedule(event_handler, "./layers/", recursive=False)
    observer.start()
    atexit.register(observer.stop)
    atexit.register(observer.join)
    logger.success("Watcher ready!")
    # Wait for data to be loaded
    while mt.loader.data is None:
        time.sleep(1)
    # Then create dashboard elements and register handler hooks
    logger.info("Creating Flattened Temperature Map...")
    flattempmap_stream_handler = IncrementalFlattenedTempMapHandler(mt.client)
    flattempmap_pane = pn.pane.HoloViews(dummy_flattempmap())
    event_handler.add_plot_stream(flattempmap_stream_handler, flattempmap_pane)
    logger.info("Creating Flattened Temperature Map...")
    recenttempmap_stream_handler = MostRecentTempMapHandler(flattempmap_stream_handler)
    recenttempmap_pane = pn.pane.HoloViews(dummy_recenttempmap())
    event_handler.add_plot_stream(recenttempmap_stream_handler, recenttempmap_pane)
    # Finally, create and return dashboard object
    return pn.template.MaterialTemplate(
        site="Panel",
        title="Live PBF Dashboard",
        main=[flattempmap_pane, recenttempmap_pane],
    )


if __name__.startswith("bokeh_app"):
    app().servable()
