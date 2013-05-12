# -*- coding: utf-8 -*-
from setuptools import setup

setup(
    name = 'buzzy',
    version = '1.0.0',
    description = 'Static, dynamic blog generator',
    license = 'BSD',
    author = 'Sebastian Pawluś',
    author_email = 'sebastian.pawlus@gmail.com',

    packages=['buzzy'],
    include_package_data = True,

    install_requires = [
        'buzzy==1.0.0',
        'osome==0.1.2',
    ],

    entry_points={
        'console_scripts': [
            'buzzy = buzzy:main'
        ]
    }
)