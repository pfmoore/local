import argparse
import subprocess
import webbrowser
import urllib.request
from urllib.error import HTTPError
from pathlib import Path


DEFAULT_USERS = ["pypa", "pfmoore"]

def make_parser():
    parser = argparse.ArgumentParser(description="Open a github URL")
    parser.add_argument("user", nargs="?", help="Github username")
    parser.add_argument("project", nargs="?", help="Github project")
    parser.add_argument("id", nargs="?", help="Github issue/PR number")
    parser.add_argument("--issues", "-i", action="store_true", help="Go to the issues page")
    parser.add_argument("--pr", "--pulls", "-p", action="store_true", help="Go to the pull requests page")
    parser.add_argument("--remote", "-r", default="origin", help="Remote to open if this is a git repo")
    parser.add_argument("--print", action="store_true", help="Print the URL rather than opening it")
    parser.add_argument("--test", action="store_true", help="Check the URL rather than opening it")
    return parser

def get_url(args):
    # Handle positional args
    #   Nothing
    #   project
    #   user project
    #   (also, #id can be included)

    if args.id:
        if args.id.startswith("#"):
            args.id = args.id[1:]
        else:
            raise SystemExit("Invalid issue/pr ID: no initial #")
    else:
        if args.project and args.project.startswith("#"):
            args.id = args.project[1:]
            args.project = ""
        elif args.user and args.user.startswith("#"):
            args.id = args.user[1:]
            args.user = ""

    if args.user and not args.project:
        args.project = args.user
        args.user = "pfmoore"

    if not args.user:
        url = get_remote(args.remote)
        if not url:
            raise SystemExit("Cannot identify project")
    else:
        url = f"https://github.com/{args.user}/{args.project}"

    if args.id:
        # Could be issue or pr
        for type in ["issue", "pull"]:
            attempt = f"{url}/{type}/{args.id}"
            if test(attempt):
                url = attempt
                break
        else:
            raise SystemExit(f"Invalid issue/pr ID: unknown id {args.id}")
    elif args.issues:
        url = url + "/issues"
    elif args.pr:
        url = url + "/pulls"

    return url


def get_remote(remote):
    if not Path(".git").is_dir():
        return None

    proc = subprocess.run(["git", "remote", "get-url", remote], text=True, capture_output=True)
    if proc:
        return proc.stdout.strip()

    return None


def test(url):
    req = urllib.request.Request(url, method="HEAD")
    try:
        with urllib.request.urlopen(req) as rsp:
            return rsp.getcode() == 200
    except HTTPError:
        return False


def main():
    parser = make_parser()
    args = parser.parse_args()
    url = get_url(args)

    if args.print:
        print(url)
    elif args.test:
        print(f"{url}:", "OK" if test(url) else "Does not exist")
    else:
        webbrowser.open(url)


if __name__ == "__main__":
    main()
