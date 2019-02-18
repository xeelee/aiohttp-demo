import os
import re

from setuptools import find_packages
from setuptools import setup


setup(
    name='aiohttp-demo',
    version='0.0.1',
    packages=find_packages(include=('aiohttp_demo*',)),
    include_package_data=True,
    install_requires=open('requirements.txt.lock').read(),
)
