#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Config object that reads configuration ini file.
Holds all configurable parameters.

Date: 2019
Author: M. Sam Ribeiro
"""

from __future__ import print_function

import ast
import configparser

class Config(object):
    def __init__(self, filename):

        self.filename = filename
        config = configparser.ConfigParser()

        with open(filename) as fid:
            config.readfp(fid)

        for key in config.options('Paths'):
            value = config.get('Paths', key)
            setattr(self, key, value)

        for section in ['Global', 'Figure', 'Video']:
            for key in config.options(section):
                value = ast.literal_eval(config.get(section, key))
                setattr(self, key, value)

    def set(self, key, value):
        ''' set config attribute '''
        print('Config: setting {0} to {1}'.format(key, value))
        setattr(self, key, value)


    def __str__(self):
        ''' return object's state '''
        config = []
        for attr, value in vars(self).items():
            config.append('Config: {0} = {1}'.format(attr, value))
        return '\n'.join(config)
