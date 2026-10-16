"""Fetch boundary tests; only the external gh transport is mocked."""
import json
import subprocess
import unittest
from unittest.mock import patch
import github_checks
from test_github_checks import fixture, SHA, RUN


class FetchGateTest(unittest.TestCase):
    def test_fetch_errors_and_partial_pages_deny_without_merge(self):
        self.assertTrue(hasattr(github_checks, 'evaluate'), 'fetch-to-deny gate missing')
        data = fixture()
        pages = [dict(total_count=2, check_runs=data['checks']), data['run'],
                 dict(total_count=2, jobs=data['jobs'])]
        cases = [pages]
        for index in (0, 2):
            partial = [dict(page) for page in pages]
            partial[index]['total_count'] = 101
            cases.append(partial)
        for error in (subprocess.CalledProcessError(1, ['gh']),
                      subprocess.TimeoutExpired(['gh'], 30),
                      json.JSONDecodeError('invalid', '', 0)):
            for index in range(3):
                cases.append(pages[:index] + [error])
        for index, responses in enumerate(cases):
            calls = []
            with self.subTest(index=index), patch.object(github_checks, 'api', side_effect=responses):
                result = github_checks.evaluate(SHA, RUN, SHA, lambda: calls.append('merge'))
                self.assertEqual(result, 'REVIEW_REJECTED' if index == 0 else 'CI_REJECTED')
                self.assertEqual(calls, [])
