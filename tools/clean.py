import shutil

from argparse import ArgumentParser
from pathlib import Path

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("target", nargs="?", help="Target directory for the build")
    args = parser.parse_args()

    base = Path(__file__).parent.parent
    if args.target:
        base = Path(args.target)

    tools = base / "tools"
    scripts = base / "scripts"

    lib = scripts / "__pypackages__/lib"
    if lib.is_dir():
        print("Removing the script dependencies")
        shutil.rmtree(lib)
    else:
        print("Script dependencies not installed")
    # Also remove pycache directory
    pycache = scripts / "__pypackages__/__pycache__"
    if pycache.is_dir():
        shutil.rmtree(pycache)

    links = [
        link for link in scripts.glob("*.exe")
        if link.is_symlink() and link.readlink().name.startswith("pylaunch")
    ]
    launchers = list(tools.glob("pylaunch*.exe"))
    if not links and not launchers:
        print("No launchers to remove")
    if links:
        print("Removing launcher links")
        for link in links:
            link.unlink()
    if launchers:
        print("Removing launchers")
        for launcher in launchers:
            launcher.unlink()
