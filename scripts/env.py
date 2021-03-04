from argparse import ArgumentParser
import subprocess
import os

p = ArgumentParser()
p.add_argument("--ignore-environment", "-i", action="store_true")
p.add_argument("--null", "-0", action="store_true")
p.add_argument("--unset", "-u", action="append", metavar="NAME")
p.add_argument("rest", nargs="*", metavar="NAME=VAL")
p.add_argument("dummy", nargs="*", metavar="COMMAND")
args = p.parse_args()

assignments = []
command = []
pusher = assignments.append
for arg in args.rest:
    if "=" not in arg:
        pusher = command.append
    pusher(arg)

if args.ignore_environment:
    env = {}
else:
    env = os.environ.copy()

if args.unset:
    for var in args.unset:
        del env[var]

for asg in assignments:
    name, _, val = asg.partition("=")
    env[name] = val

if not command:
    for name in sorted(env):
        print(f"{name}={env[name]}", end=("\0" if args.null else "\n"))
else:
    subprocess.run(command, env=env)

