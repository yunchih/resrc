#!/usr/bin/env python3
from setuptools import setup, find_packages

setup(name='logind-hook',
      version='1.1',
      description='Limit total system resources available to a user within all her sessions.',
      url='http://github.com/yunchih/logind-hook',
      author='Yunchih Chen',
      author_email='yunchih@csie.ntu.edu.tw',
      license='MIT',
      packages = ['lib'],
      install_requires=['PyYAML','dbus-python'],
      scripts=['bin/logind-hook'],
      zip_safe=True)
