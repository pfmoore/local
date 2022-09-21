import os
import sys
from pathlib import Path

lib = Path(__file__).parent / "lib"
if lib.is_dir():
    sys.path.insert(0, str(lib))

    def add_env():
        os.environ["PYTHONPATH"] = str(lib)
        bin = lib / "bin"
        if bin.is_dir():
            os.environ["PATH"] = os.environ["PATH"] + os.pathsep + str(bin)
else:
    def add_env():
        pass
