import os
from setuptools import setup, find_packages

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

with open('requirements.txt') as f:
    REQUIRED = f.read().splitlines()

# allow setup.py to be run from any path
os.chdir(
    os.path.normpath(
        os.path.join(os.path.abspath(__file__), os.pardir)
    )
)

setup(
    name='django-lessons',
    version='1.0.0',
    packages=find_packages(),
    # This (include_package_data=True) tells setuptools to install any data
    # files it finds in your packages. The data files must be specified via
    # the distutils’ MANIFEST.in file. (They can also be tracked by a
    # revision control system, using an appropriate plugin.
    include_package_data=True,
    license='Apache 2.0 License',
    description='Web based application to host django lessons',
    long_description=README,
    url='https://www.django-lessons.com/',
    author='Eugen Ciur',
    author_email='eugen@django-lessons.com',
)
