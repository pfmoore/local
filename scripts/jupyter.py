import __pypackages__
import runpy

__pypackages__.add_env()

runpy.run_module("jupyter", run_name="__main__")
