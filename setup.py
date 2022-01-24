
# -*- coding: utf-8 -*-
from setuptools import setup

long_description = None

setup_kwargs = {
    'name': 'azure-appservice-deployer',
    'version': 'v0.0.1',
    'description': 'Azure App Service file deployer',
    'long_description': long_description,
    'license': 'MIT',
    'author': 'Fabio Felici',
    'author_email': 'Fabio Felici <fabio.felici96c@gmail.com>',
    'maintainer': 'Fabio Felici',
    'maintainer_email': 'Fabio Felici <fabio.felici96c@gmail.com>',
    'url': '',
    'packages': [
        'appsrvdeployer.modules',
    ],
    'package_data': {'': ['*']},
    'python_requires': '>=3.8',

}


setup(**setup_kwargs)
