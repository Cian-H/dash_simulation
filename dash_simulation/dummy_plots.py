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
    return (dummy_overalltempdist() + dummy_recenttempdist()).opts(shared_axes=True)


def dummy_tempplots():
    return dummy_tempmaps(), dummy_tempdists()


@lru_cache(maxsize=1)
def dummy_stats_df():
    return pd.DataFrame.from_dict(
        {
            "Z (mm)": [0.04, 0.08, 0.12, 0.16, 0.2, 0.24, 0.28],
            "Min": [728.0, 735.0, 723.0, 728.0, 728.0, 728.0, 723.0],
            "Max": [1264.0, 1288.0, 1267.0, 1268.0, 1271.0, 1284.0, 1260.0],
            "Mean": [
                858.425999,
                890.300187,
                900.911889,
                906.276212,
                910.341895,
                912.550033,
                907.291338,
            ],
            "Std Dev": [
                85.033514,
                112.039592,
                118.569348,
                120.379642,
                120.873419,
                122.522130,
                121.256492,
            ],
            "Std Err": [0.079977, 0.104352, 0.109861, 0.111319, 0.111150, 0.111660, 0.108149],
            "CI Err": [0.075978, 0.099134, 0.104368, 0.105753, 0.105593, 0.106077, 0.102741],
            "CI Min": [
                858.350021,
                890.201053,
                900.807521,
                906.170458,
                910.236302,
                912.443956,
                907.188597,
            ],
            "CI Max": [
                858.501977,
                890.399321,
                901.016256,
                906.381965,
                910.447487,
                912.656110,
                907.394080,
            ],
        },
    ).set_index("Z (mm)", drop=True)
