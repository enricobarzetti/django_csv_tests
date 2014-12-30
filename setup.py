import os
from setuptools import setup, find_packages
import django_csv_tests as app

install_requires = [
    'Django >= 1.5',
]


def read(fname):
    try:
        return open(os.path.join(os.path.dirname(__file__), fname)).read()
    except IOError:
        return ''

setup(
    name='django_csv_tests',
    version=app.__version__,
    description='This allows you to define Django units tests using requests to the Django testing client in a spreadsheet format.',
    long_description=read('README.rst'),
    license='The MIT License',
    platforms=['OS Independent'],
    keywords='django',
    author='Enrico Barzetti',
    author_email='enricobarzetti@gmail.com',
    url='https://github.com/enricobarzetti/django_csv_tests',
    packages=find_packages(),
    include_package_data=True,
    install_requires=install_requires,
)
