#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
from datetime import datetime


class MockDateTime(datetime):
    ts = 12345.06789

    def timestamp(self):
        return MockDateTime.ts


def mock_randint(return_value):
    def func(a, b):
        return return_value

    return func
