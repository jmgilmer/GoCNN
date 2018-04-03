#!/usr/bin/env python
# If you get package issues trying to run main.py try this.
# You'll need to setup GoCNN in ~/src/GoCNN.
# If it can't find gomill clone https://github.com/mattheww/gomill
# and copy gomill/gommil in ~/src
# 
# Must be a better way to do this, i don't know python.

import os
import sys

# Find python packages in ~/src
sys.path.append(os.environ['HOME'] + '/src')

import GoCNN.visualization.main

GoCNN.visualization.main.gtp_io()
