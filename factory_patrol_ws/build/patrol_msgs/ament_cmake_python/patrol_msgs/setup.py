from setuptools import find_packages
from setuptools import setup

setup(
    name='patrol_msgs',
    version='0.0.0',
    packages=find_packages(
        include=('patrol_msgs', 'patrol_msgs.*')),
)
