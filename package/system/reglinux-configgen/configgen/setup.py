#!/usr/bin/env python3

from setuptools import setup, find_packages

# Package version
VERSION = '0.0.1'

setup(
    # Basic package metadata
    name='reglinux-configgen',
    version=VERSION,

    # Package discovery - automatically finds all packages
    # Excludes test packages and development files
    packages=find_packages(exclude=['tests*', 'docs*']),

    # Package dependencies
    install_requires=[
        "PyYAML>=6.0.2",        # For YAML config files
        "lxml>=5.3.2",          # For XML parsing
        "ffmpeg-python>=0.2.0", # For video conversion
        "configobj>=5.0.6",     # For INI file handling
        "requests>=2.22.0",     # For HTTP requests
        "toml>=0.10.2"          # For TOML file handling
    ],

    # Non-Python files to include (gamepad configs, etc.)
    package_data={
        'configgen.generators.xash3d_fwgs': ['gamepad.cfg'],
        # Add other data files here as needed
    },

    # Python version requirements
    python_requires='>=3.12',

    # Console script entry point
    # Creates 'reglinux-configgen' command that calls configgen:main
    entry_points={
        'console_scripts': [
            'reglinux-configgen=configgen:main',
        ],
    },
)
