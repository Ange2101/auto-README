#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from importlib.metadata import version

try:
    __version__ = version("auto-README")

except PackageNotFoundError:
    __version__ = "0.1.0"

__all__ = ["__version__"]