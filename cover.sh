#!/bin/bash
coverage run --source=tested setup.py test
coverage html
firefox htmlcov/index.html
