from functools import lru_cache
import holoviews as hv
import holoviews.operation.datashader as hd
import pandas as pd


@lru_cache(maxsize=1)
def dummy_df():
    return pd.DataFrame.from_dict({"x": [], "y": [], "z": [], "t": []})


@lru_cache(maxsize=1)
def dummy_tempmap():
    return hd.dynspread(hd.rasterize(hv.Points(dummy_df()))).opts(xlim=(30, 140), ylim=(-150, -40))


@lru_cache(maxsize=1)
def dummy_tempdist():
    return hv.Distribution(dummy_df()["t"])  # .opts(xlim=(35, 140), ylim=(-160, -30))


def dummy_flattempmap():
    return dummy_tempmap().apply.opts(title="Overall Temperature Map")


def dummy_recenttempmap():
    return dummy_tempmap().apply.opts(title="Most Recent Layer Temperature Map")


def dummy_tempmaps():
    return dummy_flattempmap() + dummy_recenttempmap()


def dummy_tempdistributions():
    return dummy_tempdist().apply.opts(
        height=300, title="Overall Temperature Distribution"
    ) + dummy_tempdist().apply.opts(height=300, title="Most Recent Layer Temperature Distribution")


def dummy_tempplots():
    return (dummy_tempmaps() + dummy_tempdistributions()).cols(2)


@lru_cache(maxsize=1)
def dummy_stats_df():
    return pd.DataFrame.from_dict(
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
    )
