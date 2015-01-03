import os

from django.test import TestCase

from django_csv_tests import generate_tests


class TheTestCase(TestCase):
    def setUp(self):
        pass


csv_path = os.path.join(os.path.dirname(__file__), 'tests.csv')
generate_tests(csv_path, TheTestCase)
