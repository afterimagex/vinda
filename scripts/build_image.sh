#!/bin/bash

set -e

conda create -n vinda python==3.10.14

conda activate vinda

pip install cython

python setup.py bdist_wheel