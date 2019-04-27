#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import os
import sys

from cx_metrics import DEFAULT_SETTINGS_MODULE

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", DEFAULT_SETTINGS_MODULE)
    from django.core.management import execute_from_command_line  # NOQA

    execute_from_command_line(sys.argv)
