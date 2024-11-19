from typing import Any, Iterable, Optional, Tuple

from datashader.reductions import Reduction
from holoviews.element.chart import Chart
import pandas as pd

from mtpy.vis.vis2d.plotter import Plotter
from mtpy.vis.vis2d.dispatchers import guarded_dispatchparams, plot_dispatch


class PatchedPlotter(Plotter):
    def plot(
        self: "Plotter",
        *args: Any,
        filename: Optional[str] = None,
        kind: str,
        add_to_dashboard: bool = False,
        samples: Optional[int | Iterable[int]] = None,
        xrange: Tuple[Optional[float], Optional[float]] | Optional[float] = None,
        yrange: Tuple[Optional[float], Optional[float]] | Optional[float] = None,
        zrange: Tuple[Optional[float], Optional[float]] | Optional[float] = None,
        groupby: Optional[str | Iterable[str]] = None,
        aggregator: Optional[Reduction] = None,
        **kwargs: Any,
    ) -> Chart:
        """Creates a 2d plot.

        Args:
            *args (Any): additional positional arguments to be passed to the plotting function
            filename (Optional[str], optional): file path to save plot to, if desired.
                Defaults to None.
            kind (str): the kind of plot to produce
            add_to_dashboard (bool, optional): the dashboard to add the plot to, if
                desired Defaults to False.
            samples (Optional[int | Iterable[int]], optional): the samples to include on the plot.
                Defaults to None.
            xrange (Tuple[Optional[float], Optional[float]] | Optional[float], optional): the range
                of x values to plot. Defaults to None.
            yrange (Tuple[Optional[float], Optional[float]] | Optional[float], optional): the range
                of y values to plot. Defaults to None.
            zrange (Tuple[Optional[float], Optional[float]] | Optional[float], optional): the range
                of z values to plot. Defaults to None.
            groupby (Optional[str | Iterable[str]], optional): the groupby to apply to the dataframe
                before plotting. Defaults to None.
            aggregator (Optional[Reduction], optional): the aggregator to apply to the plot.
                Defaults to None.
            **kwargs (Any): additional keyword arguments to be passed to the plotting
                function

        Returns:
            Chart: a holoviz plot

        Raises:
            ValueError: If given `axis_range` is invalid for `axis`
        """
        from mtpy.utils.type_guards import guarded_str_key_dict

        stream = kwargs.pop("stream")  # NOTE: Temporary bypass of logic for this param

        _kwargs = guarded_dispatchparams(kwargs)

        # generate a view id string for caching views
        view_id = self.generate_view_id(
            kind,
            samples,
            guarded_str_key_dict(_kwargs),
            xrange,
            yrange,
            zrange,
            groupby,
        )

        dummy_chunk = pd.DataFrame.from_dict({"x": [], "y": [], "z": [], "t": []})
        func_list, kwargs_list, opts = plot_dispatch(
            kind, dummy_chunk, aggregator, **_kwargs
        )

        func_iterator = zip(func_list, kwargs_list, strict=False)
        stream_func, stream_kwargs = next(func_iterator)
        plot = stream_func(dummy_chunk, **stream_kwargs)
        for func, plot_kwargs in func_iterator:
            plot = func(
                plot,
                streams=[stream],  # NOTE: Here we re-inject the streams
                **plot_kwargs,
            )
        plot = plot.opts(**opts)

        self.views[view_id] = plot

        # If filename is given, save to that file
        if filename is not None:
            import holoviews as hv

            self.logger.info(f"Saving to {filename}...")
            hv.save(plot, filename)
            self.logger.info(f"{filename} saved!")

        # # If adding to dashboard, add this plot to the dashboard
        # if add_to_dashboard and self.dashboard:
        #     self.add_to_dashboard(plot)

        # Finally, return the plot for viewing, e.g. in jupyter notebook
        return plot
