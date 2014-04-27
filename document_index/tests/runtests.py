#!/usr/bin/env python
"""
Setup a fake Django environment to run tests.
"""
import sys
from django.conf import settings
import settings as test_settings

if not settings.configured:
    settings.configure(**test_settings.__dict__)

from django_coverage.coverage_runner import CoverageRunner
from django_nose import NoseTestSuiteRunner

class NoseCoverageTestRunner(CoverageRunner, NoseTestSuiteRunner):
    """Custom test suite runner using nose and coverage."""
    pass

def runtests(*args):
    failures = NoseCoverageTestRunner(verbosity=2, interactive=True).run_tests(
            args)
    sys.exit(failures)

if __name__ == '__main__':
    runtests(*sys.argv[1:])
