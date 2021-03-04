import webbrowser
import subprocess

def run(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode:
        raise SystemExit(p.stderr.strip())
    return p.stdout.strip()

url = run(["git", "remote", "get-url", "origin"])
branch = run(["git", "branch", "--show-current"])
webbrowser.open(f"{url}/pull/new/{branch}")
