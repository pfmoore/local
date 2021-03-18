import os
import sys
from pathlib import Path

sys.path.append(os.path.join(os.path.dirname(__file__), "pyrepl-deps.zip"))

from rich import print, pretty
pretty.install()