Django CSV Tests
================

This allows you to use a spreadsheet to define Django units tests that make requests to the Django testing client.  Inspired by Robot Framework.

Installation
------------

To get the latest stable release from PyPi

.. code-block:: bash

    pip install django_csv_tests

Install the app

.. code-block:: python

    INSTALLED_APPS = (
        ...,
        'django_csv_tests',
    )

Usage
-----


Settings
--------


Mechanism
---------

Todo
----

- Implement log in and log out features.
- Implement "expect context", "expect session", and "expect" directives.

Run Tests
---------

.. code-block:: bash

    ./configure.sh
    source venv/bin/activate
    python django_csv_tests/tests/manage.py test
