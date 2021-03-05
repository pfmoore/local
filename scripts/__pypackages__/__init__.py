import sys
from pathlib import Path

lib = Path(__file__).parent / "lib"
if lib.is_dir():
    sys.path.insert(0, str(lib))
