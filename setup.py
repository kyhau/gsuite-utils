from setuptools import setup, find_packages
import os

# Makes setup work inside of a virtualenv
use_system_lib = True
if os.environ.get("BUILD_LIB") == "1":
    use_system_lib = False

base_dir = os.path.dirname(__file__)
__title__ = "gsuite-utils"
__version__ = "0.1.0.dev1"
__summary__ = "G Suite Utils."
__author__ = "Kay Hau"
__requirements__ = [
    "google-api-python-client==2.51.0",
    "oauth2client==4.1.3",
]

with open(os.path.join(base_dir, "README.md")) as f:
    long_description = f.read()

entry_points = {
    'console_scripts': [
        'gcalendar-helper = gsuite_utils.gcalendar:main',
        'gdrive-helper = gsuite_utils.gdrive:main',
    ]
}
setup(
    name=__title__,
    version=__version__,
    description=__summary__,
    long_description=long_description,
    packages=find_packages(exclude=['tests']),
    author=__author__,
    zip_safe=False,
    install_requires=__requirements__,
    entry_points=entry_points,
)
