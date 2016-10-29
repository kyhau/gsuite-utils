from __future__ import absolute_import, division, print_function
from setuptools import setup, find_packages
import os

# Makes setup work inside of a virtualenv
use_system_lib = True
if os.environ.get("BUILD_LIB") == "1":
    use_system_lib = False


base_dir = os.path.dirname(__file__)
__title__ = "gdrive-tools"
__author__ = "Kay Hau"


__about__ = {}
with open(os.path.join(base_dir, __title__, "__about__.py")) as f:
    exec(f.read(), __about__)

with open(os.path.join(base_dir, "README.md")) as f:
    long_description = f.read()


setup(
    name=__title__,
    version=__about__['__version__'],
    description=__about__["__summary__"],
    long_description=long_description,
    packages=find_packages(exclude=['tests']),
    author=__author__,
    zip_safe=False,
    install_requires=__about__["__requirements__"],
)
