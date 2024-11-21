from functools import lru_cache
import holoviews as hv
import holoviews.operation.datashader as hd
import pandas as pd


@lru_cache(maxsize=1)
def dummy_df():
    return pd.DataFrame.from_dict({"x": [], "y": [], "z": [], "t": []})


def dummy_tempmap():
    return hd.dynspread(hd.rasterize(hv.Points(dummy_df()))).opts(
        title="Flattened Temperature Map"
    )
