#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

# Package version
VERSION = '1.4'

setup(
    # Basic package metadata
    name='batocera-configgen',
    version=VERSION,

    # Package discovery - automatically finds all packages
    # Excludes test packages and development files
    packages=find_packages(exclude=['tests*', 'docs*']),

    # Package dependencies
    install_requires=[
        'PyYAML>=5.1',      # For YAML configuration handling
        'lxml>=4.3',        # For XML processing
    ],

    # Non-Python files to include (gamepad configs, etc.)
    package_data={
        'configgen.generators.xash3d_fwgs': ['gamepad.cfg'],
        # Add other data files here as needed
    },

    # Python version requirements
    python_requires='>=3.6',

    # Console script entry point
    # Creates 'batocera-configgen' command that calls configgen:main
    entry_points={
        'console_scripts': [
            'batocera-configgen=configgen:main',
        ],
    },
)
