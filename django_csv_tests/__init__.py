from urlparse import urlparse
from urlparse import urlunparse
import csv
import json
import re

from django.http import QueryDict
from django.utils.unittest import expectedFailure

__version__ = '0.1.5'

safe_chars = re.compile(r'[\W_]', re.MULTILINE)


def python_safe(s):
    """Return a name safe to use as a python function name"""
    s = s.strip().lower()
    s = [x for x in safe_chars.split(s) if x]
    return '_'.join(s)


class PreparedRequest(object):
    def __init__(self, request_description):
        self.request_description = self.validate(request_description)

    def __call__(self, test_case_instance):
        # Use test_description to make assertions
        response = self.make_request(test_case_instance.client)
        self.expect_status(test_case_instance, response)
        self.expect_header(test_case_instance, response)
        # TODO: Not yet implemented
        # self.expect_context()
        # self.expect()

    def validate(self, request_description):
        ret = request_description
        ret['login as'] = (json.loads(ret['login as'])
                           if ret['login as'] else {})
        ret['url'] = ret['url']
        ret['method'] = ret['method'].lower()
        ret['querystring'] = (json.loads(ret['querystring'])
                              if ret['querystring'] else {})
        ret['post body'] = (json.loads(ret['post body'])
                            if ret['post body'] else {})
        ret['expect status'] = int(ret['expect status'])
        ret['expect header'] = (json.loads(ret['expect header'])
                                if ret['expect header'] else {})
        return ret

    def make_request(self, client):
        if self.request_description['login as']:
            client.login(**self.request_description['login as'])

        url = self.get_url()
        if self.request_description['method'] == 'get':
            response = client.get(url)
        elif self.request_description['method'] == 'post':
            response = client.post(url, self.request_description['post body'])

        if self.request_description['login as']:
            client.logout()
        return response

    def get_url(self):
        url = self.request_description['url']
        path_parts = list(urlparse(url))
        querystring = QueryDict('', mutable=True)
        querystring.update(self.request_description['querystring'])
        path_parts[4] = querystring.urlencode(safe='/')
        return urlunparse(path_parts)

    def expect_status(self, test_case_instance, response):
        test_case_instance.assertEqual(
            self.request_description['expect status'], response.status_code)

    def expect_header(self, test_case_instance, response):
        for k, v in self.request_description['expect header'].items():
            test_case_instance.assertEqual(v, response[k])

    def expect_context(self):
        eval(self.request_description['expect context'])

    def expect(self):
        eval(self.request_description['expect'])


class PreparedTest(object):
    def __init__(self, row_num, rows_for_test):
        self.row_num = row_num
        self.rows_for_test = rows_for_test

        test_level_attributes = self.get_test_level_attributes()
        self.test_name = test_level_attributes['test name']
        self.expect_failure = test_level_attributes['expect failure']

        self.prepared_requests = self.make_prepared_requests()

    def get_test_level_attributes(self):
        return {
            'test name': self.rows_for_test[0]['test name'],
            'expect failure': bool(self.rows_for_test[0]['expect failure']),
        }

    def make_prepared_requests(self):
        prepared_requests = []
        for request_description in self.rows_for_test:
            prepared_request = PreparedRequest(request_description)
            prepared_requests.append(prepared_request)
        return prepared_requests

    def make_test_method(self):
        def test_func(the_self):
            for prepared_request in self.prepared_requests:
                prepared_request(the_self)

        if self.expect_failure:
            test_func = expectedFailure(test_func)

        test_name = 'test_csv_{}_{}'.format(self.row_num,
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
            prepared_test = PreparedTest(row_num, rows_for_test)
            prepared_tests.append(prepared_test)

    return prepared_tests


def generate_tests(csv_path, test_class):
    prepared_tests = csv_to_tests(csv_path, test_class)
    for prepared_test in prepared_tests:
        test_func = prepared_test.make_test_method()
        setattr(test_class, test_func.__name__, test_func)
