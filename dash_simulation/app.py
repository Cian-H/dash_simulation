import atexit
from bokeh.models.widgets.tables import NumberFormatter
from loguru import logger
import panel as pn
import time
from watchdog.observers import Observer
import sys

from dash_simulation.dummy_plots import dummy_stats_df, dummy_tempplots
from dash_simulation.handlers import TemperaturePlotHandler, LayerHandler, TableHandler
from dash_simulation.patched_composite import PatchedComposite


logger.remove()
logger.add(sys.stderr, colorize=True)
logger.add(open("app.log", "w"))
atexit.register(lambda: logger.warning("Closing python interpreter"))
pn.extension("plotly", "perspective")


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
    logger.info("Creating Temperature Maps tab...")
    tempplot_stream_handler = TemperaturePlotHandler(mt)
    dummy_scatters, dummy_dists = dummy_tempplots()
    tempscatters_pane = pn.pane.HoloViews(dummy_scatters)
    tempdists_pane = pn.pane.HoloViews(dummy_dists)
    tempplots_panes = (tempscatters_pane, tempdists_pane)
    event_handler.add_plot_stream(tempplot_stream_handler, tempplots_panes)
    logger.info("Creating Layer Statistics tab...")
    dsdf = dummy_stats_df()
    dsdf_fmt = {c: NumberFormatter(format="0.00") for c in ("Z (mm)", *dsdf.columns)}
    table_pane = pn.widgets.DataFrame(dsdf, sortable=True, formatters=dsdf_fmt)
    table_handler = TableHandler(mt.client)
    logger.info("Creating chat interface...")
    event_handler.add_plot_stream(table_handler, table_pane)
    chat = pn.chat.ChatInterface(show_undo=False, show_rerun=False)
    logger.info("Arranging layout...")
    plots_page = pn.Column(tempscatters_pane, tempdists_pane, sizing_mode="stretch_height")
    table_page = table_pane
    tabs = pn.Tabs(("Temperature Maps", plots_page), ("Layer Statistics", table_page))
    page = pn.Row(tabs, chat)
    logger.success("Panel generated!")
    return pn.template.MaterialTemplate(
        site="Meltpool Tomography",
        title="Live PBF Dashboard",
        logo="assets/logo.png",
        main=[page],
    )


if __name__.startswith("bokeh_app"):
    app().servable()
