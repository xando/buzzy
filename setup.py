# -*- coding: utf-8 -*-
from setuptools import setup, find_packages


setup(
    name = 'buzzy',
    version = '0.5.2',
    description = 'Static site generator',
    license = 'BSD',
    author = 'Sebastian Pawluś',
    author_email = 'sebastian.pawlus@gmail.com',
    url="http://buzzy.xando.org",
    packages=find_packages(),
    include_package_data = True,
    install_requires = [
        'watchdog==0.7.1'
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