# -*- coding: utf-8 -*-
from setuptools import setup

setup(
    name = 'buzzy',
    version = '1.0.0',
    description = 'Static, dynamic blog generator',
    license = 'BSD',
    author = 'Sebastian Pawluś',
    author_email = 'sebastian.pawlus@gmail.com',

    include_package_data = True,
    py_modules = ['buzzy'],

    install_requires = [
        'Markdown==2.3.1',
        'Pygments==1.6',
        'buzzy==1.0.0',
        'osome==0.1.0',
    ],

    entry_points={
        'console_scripts': [
            'buzzy = buzzy:main'
        ]
    }
)