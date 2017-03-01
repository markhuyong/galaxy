# -*- coding: utf-8 -*-
#!/usr/bin/python
from setuptools import setup, find_packages
from os.path import join, dirname

with open(join(dirname(__file__), 'rest/VERSION'), 'rb') as f:
    version = f.read().decode('ascii').strip()

setup(
    name="rest",
    version=version,
    author='lebooks',
    author_email='info@lebooks.com',
    url="https://github.com/lebooks/rest",
    maintainer='lebooks',
    maintainer_email='info@lebooks.com',
    description='Put Scrapy spiders behind an HTTP API',
    long_description=open('README.rst').read(),
    license='BSD',
    packages=find_packages(),
    entry_points={
        'console_scripts': ['rest = rest.cmdline:execute']
    },
    zip_safe=False,
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Operating System :: OS Independent',
        'Environment :: Console',
        'Environment :: No Input/Output (Daemon)',
        'Topic :: Internet :: WWW/HTTP',
        'License :: OSI Approved :: BSD License',
    ],
    install_requires=[
        'Twisted>=14.0.0',
        'Scrapy>=1.0.0',
        'demjson'
    ],
    package_data={
        'rest': [
            'VERSION',
        ]
    },
)
