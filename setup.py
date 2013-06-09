# -*- coding: utf-8 -*-
from setuptools import setup

setup(
    name = 'buzzy',
    version = '0.4',
    description = 'Static site generator',
    license = 'BSD',
    author = 'Sebastian Pawluś',
    author_email = 'sebastian.pawlus@gmail.com',
    url="http://buzzy.xando.org",
    packages=['buzzy'],
    include_package_data = True,

    install_requires = [
        'osome==0.1.2',
        'Jinja2==2.6'
    ],
    zip_safe=False,
    keywords = "website static generator",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 2.7'
    ]
)