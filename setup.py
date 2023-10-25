import os
from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name="logbeam",
    version="1.0",
    author="Shlomo Matichin",
    author_email="shlomi@stratoscale.com",
    description=(
        "Log posting made for automated tests environment: the framework "
        "can publish logs without knowing where and how they are stored"),
    keywords="testing automation logs",
    url="http://packages.python.org/logbeam",
    packages=['logbeam'],
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Topic :: Utilities",
    ],
    install_requires=[
        "ftputil",
        "pyftpdlib",
        "Twisted==23.8.0",
    ],
    zip_safe=False,
)
