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


class PreparedRequest(object):
    def __init__(self, test_class, request_description):
        self.test_class = test_class
        self.request_description = request_description

    def __call__(self):
        # Use test_description to make assertions
        response = self.make_request()
        self.expect_status(response)
        self.expect_header(response)
        # self.expect_context()
        # self.expect()

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


class PreparedTest(object):
    def __init__(self, test_class, row_num, rows_for_test):
        self.test_class = test_class
        self.row_num = row_num
        self.rows_for_test = rows_for_test

        test_level_attributes = self.get_test_level_attributes()
        self.test_name = test_level_attributes['test name']
        self.expect_failure = test_level_attributes['expect failure']
        self.prepared_requests = self.make_prepared_requests()

    def get_test_level_attributes(self):
        return {
            'test name': self.rows_for_test[0]['test name'],
            'expect failure': self.rows_for_test[0]['expect failure'],
        }

    def make_prepared_requests(self):
        prepared_requests = []
        for request_description in self.rows_for_test:
            prepared_request = PreparedRequest(self.test_class,
                                               request_description)
            prepared_requests.append(prepared_request)
        return prepared_requests

    def make_test_method(self):
        def test_func(self):
            for prepared_request in self.prepared_requests:
                prepared_request()

        if self.expect_failure:
            test_func = expectedFailure(test_func)

        test_name = 'csv_test_{}_{}'.format(self.row_num,
                                            python_safe(self.test_name))
        test_func.__name__ = test_name
        test_func.funcname = test_name

        return test_func


def group_by_tests(reader):
    ret = []
    for index, row in enumerate(reader):
        row_num = index + 1 + 1
        # Look at the next row to see if it is of the same test
        if not row['test name']:
            ret[-1][-1].append(row)
        else:
            new_test = [row]
            ret.append([row_num, new_test])
    return ret


def csv_to_tests(csv_path, test_class):
    prepared_tests = []
    with open(csv_path, 'rU') as f:
        reader = csv.DictReader(f)
        for row_num, rows_for_test in group_by_tests(reader):
            prepared_test = PreparedTest(test_class, row_num, rows_for_test)
            prepared_tests.append(prepared_test)

    return prepared_tests


def generate_tests(csv_path, test_class):
    prepared_tests = csv_to_tests(csv_path, test_class)
    for prepared_test in prepared_tests:
        test_func = prepared_test.make_test_method()
        setattr(test_class, test_func.__name__, test_func)
