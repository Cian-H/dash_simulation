from mtpy import MeltpoolTomography
from mtpy.proc.statistics import Statistics

from mtpy.vis.vis2d.plotter import Plotter
from dash_simulation.patched_loader import PatchedAconityLoader


class PatchedComposite(MeltpoolTomography):
    def __init__(self, client=None):
        self.loader = PatchedAconityLoader(client)
        if client is not None:
            self.cluster = client.cluster
        self.plotter = Plotter(self.loader)
        self.processor = Statistics(self.loader)
