import atexit
from loguru import logger
import panel as pn
import pandas as pd
import time
from watchdog.observers import Observer
import sys

from dash_simulation.dummy_plots import dummy_flattempmap, dummy_recenttempmap, dummy_tempscatter
from dash_simulation.handlers import (
    CombinedTempMapHandler,
    LayerHandler,
    TableHandler,
    TempScatterHandler,
)
from dash_simulation.patched_composite import PatchedComposite


logger.remove()
logger.add(sys.stderr, colorize=True)
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
    tempmap_stream_handler = CombinedTempMapHandler(mt.client)
    tempmap_pane = pn.pane.HoloViews(dummy_flattempmap() + dummy_recenttempmap())
    event_handler.add_plot_stream(tempmap_stream_handler, tempmap_pane)
    logger.info("Creating Temperature Scatter...")
    tempscatter_stream_handler = TempScatterHandler()
    tempscatter_pane = pn.pane.HoloViews(dummy_tempscatter())
    event_handler.add_plot_stream(tempscatter_stream_handler, tempscatter_pane)
    graph_column = pn.Column(tempmap_pane, tempscatter_pane)
    table_panel = pn.pane.DataFrame(
        pd.DataFrame.from_dict(
            {
                "Z (mm)": [],
                "Min": [],
                "Max": [],
                "Mean": [],
                "Std Dev": [],
                "Std Err": [],
                "CI Err": [],
                "CI Min": [],
                "CI Max": [],
            },
        ),
        index=False,
        # sizing_mode="stretch_both",
    )
    table_handler = TableHandler(mt.client)
    event_handler.add_plot_stream(table_handler, table_panel)
    row = pn.Row(graph_column, table_panel, scroll=True, sizing_mode="stretch_both")
    # Finally, create and return dashboard object
    return pn.template.MaterialTemplate(
        site="Meltpool Tomography", title="Live PBF Dashboard", logo="assets/logo.png", main=row
    )


if __name__.startswith("bokeh_app"):
    app().servable()
