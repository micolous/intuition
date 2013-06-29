#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
	name="intuition",
	version="0.1",
	description="Library and applications to interact with OWL Intuition in Python.",
	author="Michael Farrell",
	author_email="micolous@gmail.com",
	url="https://github.com/micolous/intuition",
	license="LGPL3+",
	requires=[
		'Twisted (>=12.0.0)',
		'lxml (>=2.3)',
	],
	packages=find_packages('src'),
	package_dir={'': 'src'},
	
	
	entry_points={
		'console_scripts': [
		]
	},
	
	classifiers=[
	
	],
)

