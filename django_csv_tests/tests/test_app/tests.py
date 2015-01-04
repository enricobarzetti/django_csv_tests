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
