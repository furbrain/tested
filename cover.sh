#!/bin/bash
python3-coverage run --source=tested setup.py test
python3-coverage html
firefox htmlcov/index.html
