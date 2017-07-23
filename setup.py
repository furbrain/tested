#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name="TestEd",
      version="0.1",
      description="Python testing friendly editor",
      author="Phil Underwood",
      author_email="beardydoc@gmail.com",
      url="http://github.com/furbrain/tested",
      test_suite="tests",
      packages=find_packages(),
      )  
