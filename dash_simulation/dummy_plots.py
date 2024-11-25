from functools import lru_cache
import holoviews as hv
import holoviews.operation.datashader as hd
import pandas as pd


@lru_cache(maxsize=1)
def dummy_df():
    return pd.DataFrame.from_dict({"x": [], "y": [], "z": [], "t": []})


@lru_cache(maxsize=1)
def dummy_tempscatter():
    return (
        hd.dynspread(hd.rasterize(hv.Points(dummy_df(), kdims=["x", "y"], vdims=["t"])))
        .opts(xlim=(30, 140), ylim=(-150, -40))
        .opts(colorbar=True, cmap="plasma")
    )


@lru_cache(maxsize=1)
def dummy_tempdist():
    return hv.Distribution(dummy_df()["t"])


def dummy_overalltempscatter():
    return dummy_tempscatter().apply.opts(title="Overall Temperature Map")


def dummy_recenttempscatter():
    return dummy_tempscatter().apply.opts(title="Most Recent Layer Temperature Map")


def dummy_tempmaps():
    return (dummy_overalltempscatter() + dummy_recenttempscatter()).opts(shared_axes=True)


def dummy_overalltempdist():
    return dummy_tempdist().apply.opts(title="Overall Temperature Distribution", height=300)


def dummy_recenttempdist():
    return dummy_tempdist().apply.opts(
        title="Most Recent Layer Temperature Distribution", height=300
    )


def dummy_tempdists():
    return (dummy_overalltempdist() + dummy_overalltempdist()).opts(shared_axes=True)


def dummy_tempplots():
    return dummy_tempmaps(), dummy_tempdists()


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
