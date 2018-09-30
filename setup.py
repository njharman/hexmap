#!/usr/bin/env python
from distutils.core import setup

import hexmap

setup(
        name='hexmap',
        version=hexmap.__version__,
        description='Hexagon map library',
        long_description='Paper wargame style hexmaps.',
        license='GPL - GNU Public License',
        author='Norman J. Harman Jr.',
        author_email='njharman@gmail.com',
        url='',
        platforms='Python 3.5',
        packages=['hexmap', ],
        )
