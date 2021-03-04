from urllib.request import urlopen
import json
from argparse import ArgumentParser
from datetime import datetime

p = ArgumentParser()
p.add_argument("pkg", nargs="*")
args = p.parse_args()

def print_version(pkg):
    with urlopen(f"https://pypi.org/pypi/{pkg}/json") as f:
        data = json.load(f)
    ver = data["info"]["version"]
    reldate = min(datetime.fromisoformat(f['upload_time']) for f in data['releases'][ver])
    print(f"{pkg}: {ver} ({reldate:%Y/%m/%d})")

for pkg in args.pkg:
    print_version(pkg)
