from setuptools import setup

with open("requirements.txt", "r") as req:
    requires = [row for row in req]

setup(
    name = "rfd-discovery",
    version = "0.0.1-snapshot",
    install_requires = requires
)