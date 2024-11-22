import atexit
from loguru import logger
import panel as pn
import time
from watchdog.observers import Observer
import sys

from dash_simulation.dummy_plots import (
    dummy_flattempmap,
    dummy_recenttempmap,
    dummy_tempdistributions,
    dummy_stats_df,
)
from dash_simulation.handlers import TemperaturePlotHandler, LayerHandler, TableHandler
from dash_simulation.patched_composite import PatchedComposite


logger.remove()
logger.add(sys.stderr, colorize=True)
logger.add(open("app.log", "w"))
atexit.register(lambda: logger.warning("Closing python interpreter"))
pn.extension("plotly")


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
    logger.info("Creating Temperature Maps...")
    tempplot_stream_handler = TemperaturePlotHandler(mt)
    tempplot_pane = pn.pane.HoloViews(
        (dummy_flattempmap() + dummy_recenttempmap() + dummy_tempdistributions()).cols(2)
    )
    event_handler.add_plot_stream(tempplot_stream_handler, tempplot_pane)
    logger.info("Creating Temperature Statistics Table...")
    table_panel = pn.pane.DataFrame(dummy_stats_df(), index=False)
    table_handler = TableHandler(mt.client)
    event_handler.add_plot_stream(table_handler, table_panel)
    # Finally, create and return dashboard object
    return pn.template.MaterialTemplate(
        site="Meltpool Tomography",
        title="Live PBF Dashboard",
        logo="assets/logo.png",
        main=[tempplot_pane, table_panel],
    )


if __name__.startswith("bokeh_app"):
    app().servable()
