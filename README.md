# Quality of Life Helpers Python Package (qol-helpers)

This package contains functions and tools that help me with my workflow, and they could help you too.

## Installation
I will make this available on PyPI one day. For now, you can install it by either:

1. Through pip: `python -m pip install 'qol-helpers @ git+https://github.com/FletcherFT/qol-helpers'`
2. Add to your project requirements.txt: `qol-helpers @ git+https://github.com/FletcherFT/qol-helpers'`

## Modules
### qolhelpers.geo

Contains the LatLong object useful for converting between different representations of Latitude and Longitude.

### qolhelpers.images

Contains functions for automatically cropping images and for detecting anomalies (WIP).

### qolhelpers.utils

Use this module as an entry point for basic operations. See the following:

`python -m qolhelpers.utils -h`

`python -m qolhelpers.utils copy_images -h`

`python -m qolhelpers.utils crop_images -h`

`python -m qolhelpers.utils detect_anomalies -h`