
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup_kwargs = {
    'name': 'appservice-deployer',
    'version': '0.0.3.3',
    'description': 'Azure App Service file deployer',
    'long_description': long_description,
    'license': 'MIT',
    'author': 'Fabio Felici',
    'author_email': 'Fabio Felici <fabio.felici96c@gmail.com>',
    'maintainer': 'Fabio Felici',
    'maintainer_email': 'Fabio Felici <fabio.felici96c@gmail.com>',
    'url': '',
    'packages': [
        'appsrvdeployer',
        'appsrvdeployer.modules',
    ],
    "project_urls": {
        "homepage": "https://github.com/rhslack/appservice-deployer",
        "Bug Tracker": "https://github.com/rhslack/appservice-deployer/issues",
    },
    "classifiers": [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    'package_data': {'': ['*']},
    'python_requires': '>=3.8',
    "package_dir": {"": "src"},
}


setup(**setup_kwargs)
