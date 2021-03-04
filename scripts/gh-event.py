import __pypackages__
import requests
import subprocess
from urllib.parse import urlparse
from argparse import ArgumentParser
import json

p = ArgumentParser()
p.add_argument("--payload-json", help="The complete client payload, in JSON format")
p.add_argument("type", help="The event type")
p.add_argument("payload", nargs="*", help="Payload values, in the form NAME=VALUE")
args = p.parse_args()

payload = {}
if args.payload_json:
    if args.payload:
        raise SystemError("Cannot specify both key/value and JSON payload values")
    payload = json.loads(args.payload_json)
elif args.payload:
    for item in args.payload:
        key, sep, val = item.partition("=")
        if sep != "=":
            raise SystemError(f"Payload values must have the form KEY=VALUE: {item}")
        payload[key] = val

data = { "event_type": args.type }
if payload:
    data["client_payload"] = payload

origin = subprocess.run(
    ["git", "remote", "get-url", "origin"],
    check=True,
    stdout=subprocess.PIPE,
    text=True,
).stdout.strip()

cred = subprocess.run(
    ["git", "credential", "fill"],
    input=f"url={origin}",
    check=True,
    stdout=subprocess.PIPE,
    text=True,
).stdout

credentials = dict(line.split("=") for line in cred.splitlines())
token = credentials["password"]


headers = {
    "Accept": "application/vnd.github.everest-preview+json",
    "Content-Type": "application/json",
    "Authorization": f"Bearer {token}",
}
path = urlparse(origin).path
url = f"https://api.github.com/repos{path}/dispatches"
r = requests.post(url, headers=headers, json=data)
