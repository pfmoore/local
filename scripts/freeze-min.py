import __pypackages__
import importlib.metadata
from packaging.requirements import Requirement
import re

def normalize(name):
    return re.sub(r"[-_.]+", "-", name).lower()

dependencies = set()
all_packages = set()
for dist in importlib.metadata.distributions():
    name = normalize(dist.metadata["name"])
    all_packages.add(name)
    if dist.requires:
        for req in dist.requires:
            dep = normalize(Requirement(req).name)
            dependencies.add(dep)

top_level = all_packages - dependencies
for name in sorted(top_level):
    print(f"{name}=={importlib.metadata.version(name)}")
