# -*- coding: utf-8 -*-
from setuptools import setup

setup(
    name = 'buzzy',
    version = '1.0.2',
    description = 'Static site generator',
    license = 'BSD',
    author = 'Sebastian Pawluś',
    author_email = 'sebastian.pawlus@gmail.com',

    packages=['buzzy'],
    include_package_data = True,

    install_requires = [
        'osome==0.1.2',
        'Jinja2==2.6'
    ],

    entry_points={
        'console_scripts': [
            'buzzy = buzzy:main'
        ]
    }
)