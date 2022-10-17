from setuptools import setup

setup(
   name='opendir',
   version='1.0',
   description='Simple wrapper for scraping open directories.',
   author='vxuv',
   packages=['opendir'],
   install_requires=['requests', 'bs4', 'typing'],
)