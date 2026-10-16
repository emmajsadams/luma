"""Synthetic dry-run probe; never invokes a merge API."""
import unittest
from pathlib import Path
import importlib.util

class HeadGateTest(unittest.TestCase):
    def test_stale_review_denies_merge_callback(self):
        path = Path(__file__).with_name('head_gate.py')
        self.assertTrue(path.exists(), 'deterministic head gate is missing')
        spec = importlib.util.spec_from_file_location('head_gate', path)
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        calls = []
        result = module.attempt('a' * 40, 'b' * 40, lambda: calls.append('merge'))
        self.assertEqual(result, 'STALE_HEAD_REJECTED')
        self.assertEqual(calls, [])

    def test_missing_failed_or_wrong_head_ci_denies_merge(self):
        from head_gate import attempt
        import inspect
        self.assertIn('checks', inspect.signature(attempt).parameters, 'CI evidence gate missing')
        sha = 'a' * 40
        cases = [
            [],
            [{'name': 'quality', 'head_sha': sha, 'conclusion': 'failure'}],
            [{'name': 'quality', 'head_sha': 'b' * 40, 'conclusion': 'success'}],
            [{'name': 'quality', 'head_sha': sha, 'conclusion': None}],
        ]
        browser = {'name': 'browser', 'head_sha': sha, 'conclusion': 'success'}
        quality = {'name': 'quality', 'head_sha': sha, 'conclusion': 'success'}
        cases += [case + [browser] for case in cases[1:]]
        cases += [[quality], [quality, browser, quality]]
        for checks in cases:
            with self.subTest(checks=checks):
                calls = []
                result = attempt(sha, sha, lambda: calls.append('merge'), checks=checks)
                self.assertEqual(result, 'CI_REJECTED')
                self.assertEqual(calls, [])

        calls = []
        self.assertEqual(attempt(sha, sha, lambda: calls.append('merge'),
                                 checks=[quality, browser]), 'REVIEW_REJECTED')
        self.assertEqual(calls, [])

    def test_forged_self_or_stale_reviewer_is_rejected(self):
        from head_gate import attempt
        sha = 'a' * 40
        checks = [{'name': name, 'head_sha': sha, 'conclusion': 'success'}
                  for name in ('quality', 'browser')]
        valid = {'session_id': 'review-session', 'head_sha': sha, 'verdict': 'PASS'}
        cases = [
            (None, {'review-session'}, 'build-session'),
            (dict(valid, session_id='forged'), {'review-session'}, 'build-session'),
            (dict(valid, session_id='build-session'), {'build-session'}, 'build-session'),
            (dict(valid, head_sha='b' * 40), {'review-session'}, 'build-session'),
            (dict(valid, verdict='CHANGES_REQUIRED'), {'review-session'}, 'build-session'),
            (valid, set(), 'build-session'),
            (valid, {'review-session'}, None),
        ]
        for review, registered, builder in cases:
            with self.subTest(review=review, registered=registered, builder=builder):
                calls = []
                self.assertEqual(attempt(sha, sha, lambda: calls.append('merge'),
                    checks=checks, review=review, registered_reviewers=registered,
                    builder_session=builder), 'REVIEW_REJECTED')
                self.assertEqual(calls, [])
        calls = []
        self.assertEqual(attempt(sha, sha, lambda: calls.append('merge'),
            checks=checks, review=valid, registered_reviewers={'review-session'},
            builder_session='build-session'), 'UNVERIFIED_GATES')
        self.assertEqual(calls, [])

if __name__ == '__main__':
    unittest.main()
