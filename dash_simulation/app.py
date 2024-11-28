import atexit
from bokeh.models.widgets.tables import NumberFormatter
from functools import cache
import hvplot.pandas
from loguru import logger
import panel as pn
import time
from watchdog.observers import Observer
import sys

from dash_simulation.dummy_plots import dummy_stats_df, dummy_tempplots
from dash_simulation.handlers import TemperaturePlotHandler, LayerHandler, TemperatureStatsHandler
from dash_simulation.patched_composite import PatchedComposite


logger.remove()
logger.add(sink=sys.stderr, level="DEBUG", colorize=True)
atexit.register(lambda: logger.warning("Closing python interpreter"))
pn.extension("plotly", "perspective")


@cache
def get_client():
    from dask.distributed import Client, LocalCluster

    cluster = LocalCluster()
    return Client(cluster)


def app(client=None):
    # Create observer and register hooks for handling/cleanup
    logger.info("Initialising application...")
    mt = PatchedComposite(client=client)
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
    logger.debug("Creating Temperature Maps tab...")
    tempplot_stream_handler = TemperaturePlotHandler(mt)
    dummy_scatters, dummy_dists = dummy_tempplots()
    tempscatters_pane = pn.pane.HoloViews(dummy_scatters)
    tempdists_pane = pn.pane.HoloViews(dummy_dists)
    tempplots_panes = (tempscatters_pane, tempdists_pane)
    event_handler.add_plot_stream(tempplot_stream_handler, tempplots_panes)
    logger.debug("Creating Layer Statistics tab...")
    dsdf = dummy_stats_df()
    dsdf_fmt = {c: NumberFormatter(format="0.00") for c in ("Z (mm)", *dsdf.columns)}
    table_pane = pn.widgets.DataFrame(dsdf, sortable=True, formatters=dsdf_fmt)
    explorer_pane = hvplot.explorer(dsdf)
    tempstats_handler = TemperatureStatsHandler(mt.client)
    tempstats_panes = (explorer_pane, table_pane)
    event_handler.add_plot_stream(tempstats_handler, tempstats_panes)
    logger.debug("Creating Cluster Status tab...")
    status_pane = pn.pane.HTML(
        f"""
            <iframe src="{mt.cluster.dashboard_link}" style="width: 100%; height: 100%; border: none;"></iframe>
        """,
        sizing_mode="stretch_both",
    )
    logger.debug("Creating chat interface...")
    chat = pn.chat.ChatInterface(show_undo=False, show_rerun=False, width=512)
    logger.debug("Arranging layout...")
    plots_page = pn.Column(tempscatters_pane, tempdists_pane, sizing_mode="stretch_height")
    table_page = pn.Column(explorer_pane, table_pane)
    tabs = pn.Tabs(
        ("Temperature Maps", plots_page),
        ("Layer Statistics", table_page),
        ("Cluster Status", status_pane),
        sizing_mode="scale_width",
    )
    page = pn.Row(tabs, chat)
    logger.success("Panel generated!")
    return pn.template.MaterialTemplate(
        site="Meltpool Tomography",
        title="Live PBF Dashboard",
        logo="assets/logo.png",
        main=[page],
    )


if __name__.startswith("bokeh_app"):
    app(client=get_client()).servable()
