#!/usr/bin/env python

# Accessing local commands.py
import sys
sys.path.insert(0, '../')

from optparse import make_option
from commands import CLI


class TestingCLI(CLI):
    version = '1.0'
    option_list = (
        make_option('--host', dest='host', help='Host to listen on'),
    )

if __name__ == '__main__':
    TestingCLI(packages='./methods')
