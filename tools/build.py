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
    print("Refreshing script dependencies")
    # First, remove everthing from __pypackages__
    # that isn't managed by git.
    subprocess.run([
        "git", "clean", "-f", "-X", str(packages)
    ])
    # Now install the required packages
    subprocess.run([
        sys.executable,
        "-m", "pip",
        "--disable-pip-version-check",
        "install",
        "--target", packages,
        "-r", packages / "requirements.txt"
    ])

PY_EXTENSIONS = [".py", ".pyz", ".pyw", ".pyzw"]

def refresh_launcher_links(tools: Path, target: Path):
    print(f"Refreshing launcher links in {target.relative_to(Path.cwd())}")
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

def refresh_apps(target: Path):
    # Install the required apps. We do this even without
    # rebuild, as we're upgrading in place in that case
    for app in ("shiv", "pipx", "virtualenv"):
        action = "Refreshing" if (target / f"{app}.pyz").exists() else "Installing"
        print(f"{action} application {app}")
        if app == "virtualenv":
            # Virtualenv supplies its own zipapp
            download_url(target, VIRTUALENV_URL)
        else:
            make_zipapp(target, app)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--apps", action="store_true", help="Refresh zipapps")
    parser.add_argument("--launchers", action="store_true", help="Refresh pylaunch")
    parser.add_argument("--script-deps", action="store_true", help="Refresh script dependencies")
    parser.add_argument("--launcher-links", action="store_true", help="Refresh launcher links")
    parser.add_argument("target", nargs="?", help="Target directory for the build")
    args = parser.parse_args()

    base = Path(__file__).parent.parent
    if args.target:
        base = Path(args.target)

    # If nothing specific is requested, refresh everything
    if not any((args.apps, args.launchers, args.script_deps, args.launcher_links)):
        args.apps = True
        args.launchers = True
        args.script_deps = True
        args.launcher_links = True

    apps = base / "apps"
    tools = base / "tools"
    scripts = base / "scripts"

    # Create the target directories if they aren't present
    apps.mkdir(parents=True, exist_ok=True)
    tools.mkdir(parents=True, exist_ok=True)
    scripts.mkdir(parents=True, exist_ok=True)

    if args.apps:
        refresh_apps(apps)
    if args.launchers:
        refresh_pylaunch(tools)
    if args.script_deps:
        refresh_script_dependencies(scripts)
    if args.launcher_links:
        refresh_launcher_links(tools, apps)
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
