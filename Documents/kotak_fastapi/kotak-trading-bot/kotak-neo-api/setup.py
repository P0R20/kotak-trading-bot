from setuptools import setup, find_packages

setup(
    name='neo_api_client',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'websocket-client',
        'requests'
    ],
)
