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

VIRTUALENV_URL = "https://bootstrap.pypa.io/virtualenv.pyz"

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
            "--target", os.path.join(build, "site-packages"),
            module,
            *extra_pip_args
        ])
        main = build / "__main__.py"
        main.write_text(MAIN_SCRIPT.format(module=module), encoding="utf-8")
        zipapp.create_archive(build, target / f"{module}.pyz")

def download_url(target: Path, url):
    # This is a hack, should properly parse out the basename
    _, _, filename = urlparse(url).path.rpartition('/')
    with urlopen(url) as src:
        with open(target / filename, "wb") as dst:
            shutil.copyfileobj(src, dst)

def get_pylaunch(dest: Path):
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

    with urlopen(url) as pl:
        with ZipFile(io.BytesIO(pl.read())) as z:
            z.extractall(str(dest))

def install_script_dependencies(scripts: Path):
    packages = scripts / "__pypackages__"
    subprocess.run([
        sys.executable,
        "-m", "pip",
        "--disable-pip-version-check",
        "install",
        "--upgrade",
        "--target", packages,
        "-r", packages / "requirements.txt"
    ])

PY_EXTENSIONS = [".py", ".pyz", ".pyw", ".pyzw"]

def link_launcher(tools: Path, target: Path):
    assert tools.parent == target.parent
    for script in target.glob("*.py*"):
        if script.suffix in PY_EXTENSIONS:
            launcher = script.with_suffix(".exe")
            if launcher.exists():
                # Assume this is a rebuild, and the existing link can stay.
                continue
            if script.suffix.endswith("w"):
                pylaunch = Path("..", tools.name, "pylaunchw.exe")
            else:
                pylaunch = Path("..", tools.name, "pylaunch.exe")
            launcher.symlink_to(pylaunch)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--rebuild", action="store_true", help="Rebuild existing installation")
    parser.add_argument("target", help="Target directory for the build")
    args = parser.parse_args()

    base = Path(args.target)
    src = Path(__file__).parent.parent

    apps = base / "apps"
    tools = base / "tools"
    scripts = base / "scripts"

    # Only rebuild scripts/tools if they aren't already there
    # or the user explicitly requests it.
    rebuild_tools = (args.rebuild or not tools.is_dir())
    rebuild_scripts = (args.rebuild or not scripts.is_dir())

    # Create the target directories if they aren't present
    apps.mkdir(parents=True, exist_ok=True)
    tools.mkdir(parents=True, exist_ok=True)
    scripts.mkdir(parents=True, exist_ok=True)

    # Install the required apps. We do this even without
    # rebuild, as we're upgrading in place in that case
    for app in ("shiv", "pipx", "virtualenv"):
        print(f"Application {app}.pyz is already present, updating")
        if app == "virtualenv":
            # Virtualenv supplies its own zipapp
            download_url(apps, VIRTUALENV_URL)
        else:
            make_zipapp(apps, app)

    # Install the latest launcher. This is an upgrade in place
    # if the target exists, and any uses of the launcher will
    # be symlinks, and so will automatically pick up the new
    # version.
    get_pylaunch(tools)

    # Only replace the tools and scripts if we're doing a rebuild.
    if rebuild_tools:
        shutil.copytree(src / "tools", tools, dirs_exist_ok=True)
    if rebuild_scripts:
        shutil.copytree(src / "scripts", scripts, dirs_exist_ok=True)

    # This will upgrade script dependences if they are already installed
    # TODO: Should we delete existing dependencies on --rebuild?
    install_script_dependencies(scripts)

    # This will just add new links as needed
    # TODO: Should it re-write existing links on --rebuild?
    link_launcher(tools, apps)
    link_launcher(tools, scripts)