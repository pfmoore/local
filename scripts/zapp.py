import os
import subprocess
import sys
import zipapp
from argparse import ArgumentParser
from pathlib import Path
from tempfile import TemporaryDirectory

MAIN_SCRIPT = """\
import runpy
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "site-packages"))
runpy.run_module("{module}", run_name="__main__")
"""

def make_zipapp(target: Path, module: str, *extra_pip_args):
    with TemporaryDirectory() as build:
        build = Path(build)
        subprocess.run([
            sys.executable,
            "-m", "pip",
            "--disable-pip-version-check",
            "--quiet",
            "install",
            "--target", str(build / "site-packages"),
            module,
            *extra_pip_args
        ])
        main = build / "__main__.py"
        main.write_text(MAIN_SCRIPT.format(module=module), encoding="utf-8")
        zipapp.create_archive(build, target / f"{module}.pyz")

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--target-dir", default=".", help="Directory to save zipapp")
    parser.add_argument("module", help="Module to build as a zipapp")
    parser.add_argument("extra", nargs="*", help="Extra arguments to pip")
    args = parser.parse_args()

    target = Path(args.target_dir)
    make_zipapp(target, args.module, *args.extra)
