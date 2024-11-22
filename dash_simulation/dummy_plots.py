from functools import lru_cache
import holoviews as hv
import holoviews.operation.datashader as hd
import pandas as pd


@lru_cache(maxsize=1)
def dummy_df():
    return pd.DataFrame.from_dict({"x": [], "y": [], "z": [], "t": []})


@lru_cache(maxsize=1)
def dummy_tempmap():
    return hd.dynspread(hd.rasterize(hv.Points(dummy_df()))).opts(xlim=(35, 140), ylim=(-160, -30))


def dummy_flattempmap():
    return dummy_tempmap().apply.opts(title="Flattened Temperature Map")


def dummy_recenttempmap():
    return dummy_tempmap().apply.opts(title="Most Recent Temperature Map")


def dummy_tempscatter():
    return dummy_tempmap().apply.opts(
        xlim=(0, 100), ylim=(0, 1500), height=300, title="Overall Temperature Scatter"
    ) + dummy_tempmap().apply.opts(
        xlim=(0, 100), ylim=(0, 1500), height=300, title="Intra-Layer Temperature Scatter"
    )
