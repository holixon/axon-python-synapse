#!/usr/bin/env python

from distutils.core import setup

setup(
    name="axon-python",
    version="0.0.1",
    description="Axon Synapse Python Library",
    author="Ferhat Ayaz",
    author_email="ferhat.ayaz@holisticon.de",
    url="https://www.holisticon.de",
    packages=["axon", "axon.adapter", "axon.application", "axon.domain"],
    install_requires=["aiohttp"],
)
