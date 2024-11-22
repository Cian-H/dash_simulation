import panel as pn

from dash_simulation.app import app


if __name__ == "__main__":
    pn.serve(app(), port=4242, show=True)
