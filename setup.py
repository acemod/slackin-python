#!/usr/bin/env python3

import os
import sys
import platform
from setuptools import setup, find_packages

def read(fname):
  return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "slackin-python",
    version = "1.0",
    packages = ["slackin"],
    package_data = {
        "slackin": ["static/*", "templates/*"],
    },
    include_package_data = True,
    zip_safe = False,
    scripts = ["scripts/slackin"],
    install_requires = ["requests", "docopt", "flask", "django-htmlmin"],
    author = "Felix \"KoffeinFlummi\" Wiegand",
    author_email = "koffeinflummi@gmail.com",
    description = "Python port of the slackin Slack auto-inviter",
    long_description = read("README.md"),
    license = "MIT",
    keywords = "",
    url = "https://github.com/acemod/slackin-python",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4"
    ]
)
