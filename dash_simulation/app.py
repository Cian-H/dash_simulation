import atexit
import holoviews as hv
from loguru import logger
import panel as pn
import time
from watchdog.observers import Observer
import sys

from dash_simulation.dummy_plots import dummy_tempmap
from dash_simulation.handlers import IncrementalTempMapHandler, LayerHandler
from dash_simulation.patched_composite import PatchedComposite


logger.remove()
logger.add(sys.stderr, colorize=True)
atexit.register(lambda: logger.warning("Closing python interpreter"))


hv.extension("plotly")


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
    tempmap_stream_handler = IncrementalTempMapHandler(mt.client)
    tempmap_pane = pn.pane.HoloViews(dummy_tempmap())
    event_handler.add_plot_stream(tempmap_stream_handler, tempmap_pane)
    return pn.template.MaterialTemplate(
        site="Panel",
        title="Live PBF Dashboard",
        main=[tempmap_pane],
    )


if __name__.startswith("bokeh_app"):
    app().servable()
