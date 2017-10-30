# -*- coding: utf-8 -*- {{{
########################################################################
# Copyright (c) 2017, Intwine Connect, LLC.                            #
# This file is licensed under the BSD-3-Clause                         #
# See LICENSE for complete text                                        #
########################################################################

#}}}

from setuptools import setup, find_packages

#get environ for agent name/identifier
packages = find_packages('.')
package = packages[0]

setup(
    name = package,
    version = "1.0",
    install_requires = ['volttron'],
    packages = packages,
    entry_points = {
        'setuptools.installation': [
            'eggsecutable = ' + package + '.agent:main',
        ]
    }
)
