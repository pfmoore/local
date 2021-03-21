import os
import sys
from pathlib import Path

sys.path.append(os.path.join(os.path.dirname(__file__), "pyrepl-deps.zip"))

from rich import print, pretty
pretty.install()

# See https://discuss.python.org/t/add-a-flag-hide-magic-names-in-dir/7276/2
def ddir(obj):
    return [a + '()' if callable(getattr(obj, a)) else a
            for a in dir(obj) if not (a[:2] == '__' == a[-2:])]
