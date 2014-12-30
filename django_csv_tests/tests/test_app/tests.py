from django.test import TestCase


class ClientDataTestCase(TestCase):
    def test(self):
        response = self.client.get('/')

        # Remove the csrf key because it is not determinable
        actual = response.context['client_data']
        del actual['csrftoken']

        expected = {
            'DEBUG': False,
            'STATIC_URL': '/static/',
            'foo': 'bar',
            'url_args': (),
            'url_kwargs': {},
            'url_name': 'index',
            'user_full_name': None,
            'user_pk': None,
            'username': None
        }
        self.assertEqual(expected, actual)
