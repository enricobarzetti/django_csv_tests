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

Create a CSV file with the headers "test name", "expect failure", "login as",
"url", "method", "querystring", "post body", "expect status",
"expect header".  Then create a test file like:

.. code-block:: python

    import os

    from django.contrib.auth import get_user_model
    from django.test import TestCase

    from django_csv_tests import generate_tests


    class TheTestCase(TestCase):
        def setUp(self):
            self.user = get_user_model().objects.create_user(username='john.doe',
                                                             email='john@doe.com',
                                                             password='password')


    csv_path = os.path.join(os.path.dirname(__file__), 'tests.csv')
    generate_tests(csv_path, TheTestCase)

You can define tests as a sequence of requests with associated assertions.  A
test is defined with a test name and one or more rows that describe requests to
make.  If a row does not have a test name it indicates that the request defined
on that row is part of the last named test.

Column values
+++++++++++++

test name
~~~~~~~~~

A string used to name the test.

expect failure
~~~~~~~~~~~~~~

A boolean used to indicated whether the test is expected to fail.  Any non-zero
length string indicates True.  An easy way is enter this in a spreadsheet is as
"x".

login as
~~~~~~~~

A JSON encoded string that provides the username and password of the user to log
in as.  This is passed as keyword arguments to
django.contrib.auth.authenticate().  Example: {"username": "john.doe",
"password": "password"}.

url
~~~

The URL that the request should be made to.

method
~~~~~~

An HTTP method.  GET and POST are supported.

querystring
~~~~~~~~~~~

A JSON encoded string that contains querystring keys and values.  This becomes
``request.GET``.

post body
~~~~~~~~~

A JSON encoded string that contains data to submit in a POST request.  This is
used only if the method is POST.  This becomes ``request.POST``.

expect status
~~~~~~~~~~~~~

The HTTP status code expected for the response.

expect header
~~~~~~~~~~~~~

A JSON encoded string that contains header keys and values expected in the
response.  Example: A redirect response could have the header
{"Location": "http://testserver/new_location/"}

Todo
----

- Implement "variables", "expect context", and "expect" directives.

Variables
=========

"user_id = self.user.pk
expected = {""__all__"": ""Passwords did not match""}"

Expect context
==============

form.errors == expected

Expect
======

len(response.content) == 2000

Run Tests
---------

.. code-block:: bash

    ./configure.sh
    source venv/bin/activate
    python django_csv_tests/tests/manage.py test
