hexmap
======

Paper wargame style hexagon maps.  I use it when building tools for and
computerized versions of paper wargames.  YMMV.


Install
=======

Not on PyPI; install from git::

    uv add git+https://github.com/njharman/hexmap


Usage
=====

::

    from hexmap import Hex, BoundedHex

    h = Hex('0608')
    h.sixpack()          # surrounding hexes
    h.distance_to(Hex('1112'))


Development
===========

::

    uv sync
    uv run pytest


Copyright & License
===================

Copyright (c) 2002-2006, 2012 Norman J. Harman Jr. (njharman@gmail.com)

GPL v2 or later, see ``LICENSE``.


Testing
=======

  python -m unittest discover -s test


Installation
============

  python setup.py install
