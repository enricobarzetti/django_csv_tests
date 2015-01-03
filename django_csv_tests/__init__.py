import csv
import re
from urlparse import urlparse
from urlparse import urlunparse

from django.http import QueryDict
from django.utils.unittest import expectedFailure

__version__ = '0.1.0'

safe_chars = re.compile(r'[\W_]', re.MULTILINE)


def python_safe(s):
    """Return a name safe to use as a python function name"""
    s = s.strip().lower()
    s = [x for x in safe_chars.split(s) if x]
    return '_'.join(s)


class TestRequest(object):
    def __init__(self, test_class, request_description):
        self.test_class = test_class
        self.request_description = request_description

    def __call__(self, *args, **kwargs):
        # Use test_description to make assertions
        response = self.make_request()
        self.expect_status(response)
        self.expect_header(response)
        self.expect_context()
        self.expect()

    def make_request(self):
        url = self.get_url()
        if self.request_description['method'] == 'get':
            response = self.test_class.client.get(url)
        elif self.request_description['method'] == 'post':
            response = self.test_class.client.post(
                url, self.request_description['post body'])
        return response

    def get_url(self):
        url = self.request_description['url']
        path_parts = list(urlparse(url))
        querystring = QueryDict('', mutable=True)
        querystring.update(self.request_description['querystring'])
        path_parts[4] = querystring.urlencode(safe='/')
        return urlunparse(path_parts)

    def expect_status(self, response):
        self.test_class.assertEqual(self.request_description['expect status'],
                                    response.status)

    def expect_header(self, response):
        for k, v in self.request_description['expect header'].items():
            self.test_class.assertEqual(v, response.items()[k])

    def expect_context(self):
        eval(self.request_description['expect context'])

    def expect(self):
        eval(self.request_description['expect'])


def csv_to_tests(csv_path):
    with open(csv_path, 'rU') as f:
        reader = csv.reader(f)

        # Skip first header row
        reader.next()

        row_num = 2
    return []


def make_test(test_class,  test_description):
    test_requests = []
    # test_description is a list of dictionaries
    for request_description in test_description:
        test_request = TestRequest(test_class, request_description)
        test_requests.append(test_request)

    def test_func():
        for test_request in test_requests:
            test_request()
    test_name = 'csv_test_{}_{}'.format(
        test_description['row_num'], python_safe(test_description['test_name']))
    test_func.__name__ = test_name
    test_func.funcname = test_name

    if test_description[0]['expect failure']:
        test_func = expectedFailure(test_func)
    return test_func


def generate_tests(csv_path, test_class):
    test_descriptions = csv_to_tests(csv_path)
    for test_description in test_descriptions:
        test_func = make_test(test_class, test_description)
        setattr(test_class, test_func.__name__, test_func)


