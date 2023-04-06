import io
import json
import os
import shutil
import subprocess
import sys
import zipapp
from argparse import ArgumentParser
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.parse import urlparse
from urllib.request import urlopen
from zipfile import ZipFile

def refresh_pylaunch(dest: Path):
    USER = "pfmoore"
    PROJECT = "pylaunch"
    API_URL = f"https://api.github.com/repos/{USER}/{PROJECT}/releases/latest"
    url = None
    with urlopen(API_URL) as f:
        data = json.load(f)
        for asset in data["assets"]:
            if asset["name"] == "pylaunch.zip":
                url = asset["browser_download_url"]
    if url is None:
        raise ValueError("Could not find pylaunch release")

    if (dest / "pylaunch.exe").exists():
        print("Refreshing pylaunch launchers")
    else:
        print("Installing pylaunch launchers")

    with urlopen(url) as pl:
        with ZipFile(io.BytesIO(pl.read())) as z:
            z.extractall(str(dest))

def refresh_script_dependencies(scripts: Path):
    packages = scripts / "__pypackages__"
    lib = packages / "lib"
    if (lib.is_dir()):
        print("Refreshing script dependencies")
        shutil.rmtree(lib)
    else:
        print("Installing script dependencies")

    # Now install the required packages
    subprocess.run([
        sys.executable,
        "-m", "pip",
        "--disable-pip-version-check",
        "install",
        "--target", lib,
        "-r", packages / "requirements.txt"
    ])

PY_EXTENSIONS = [".py", ".pyz", ".pyw", ".pyzw"]

def refresh_launcher_links(tools: Path, target: Path):
    print(f"Refreshing launcher links in {target}")
    assert tools.parent == target.parent
    for script in target.glob("*.py*"):
        if script.suffix in PY_EXTENSIONS:
            if script.suffix.endswith("w"):
                pylaunch = Path("..", tools.name, "pylaunchw.exe")
            else:
                pylaunch = Path("..", tools.name, "pylaunch.exe")

            launcher = script.with_suffix(".exe")
            if launcher.exists():
                if launcher.is_symlink() and launcher.readlink() == pylaunch:
                    pass
                else:
                    print(f"Skipping {launcher.name} as it is not a launcher link")
                    continue
            else:
                launcher.symlink_to(pylaunch)

def refresh_pyrepl_deps(config: Path):
    with TemporaryDirectory() as tmp:
        subprocess.run([
            sys.executable,
            "-m", "pip",
            "--disable-pip-version-check",
            "install",
            "--target", tmp,
            "-r", config / "pyrepl-requirements.txt"
        ])
        shutil.make_archive(config / "pyrepl-deps", "zip", tmp)

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--launchers", action="store_true", help="Refresh pylaunch")
    parser.add_argument("--script-deps", action="store_true", help="Refresh script dependencies")
    parser.add_argument("--pyrepl-deps", action="store_true", help="Refresh Python REPL dependencies")
    parser.add_argument("--launcher-links", action="store_true", help="Refresh launcher links")
    parser.add_argument("target", nargs="?", help="Target directory for the build")
    args = parser.parse_args()

    base = Path(__file__).parent.parent
    if args.target:
        base = Path(args.target)

    # If nothing specific is requested, refresh everything
    if not any((args.launchers, args.script_deps, args.pyrepl_deps, args.launcher_links)):
        args.launchers = True
        args.script_deps = True
        args.pyrepl_deps = True
        args.launcher_links = True

    tools = base / "tools"
    scripts = base / "scripts"
    config = base / "config"

    # Create the target directories if they aren't present
    tools.mkdir(parents=True, exist_ok=True)
    scripts.mkdir(parents=True, exist_ok=True)
    config.mkdir(parents=True, exist_ok=True)

    if args.launchers:
        refresh_pylaunch(tools)
    if args.script_deps:
        refresh_script_dependencies(scripts)
    if args.pyrepl_deps:
        refresh_pyrepl_deps(config)
    if args.launcher_links:
        refresh_launcher_links(tools, scripts)

# TODO: Configuration files
#   * Powershell profile
#   * Windows Terminal settings
#   * Git config
#   * Keypirinha settings (scoop)
#
# TODO: Other applications
#   * Apps to be installed via pipx
#   * Scoop apps
