"""Synthetic policy tests, porting negative invariants from PR14 c2ad85e.

No authenticated sessions, GitHub transport, or merge execution is simulated.
"""
import copy
import unittest
from typing import Any

from factory_native import merge_policy as p


def fixture() -> dict[str, Any]:
    target = dict(repository='emmajsadams/luma', pr=18, issue=11,
                  revision='d' * 64, head='a' * 40, base='b' * 40)
    return dict(version=1, expected=target, current=copy.deepcopy(target),
                approved=copy.deepcopy(target), approval_scope='merge',
                builder_session='builder', registered_reviewers=['reviewer'],
                review=dict(session='reviewer', head=target['head'], verdict='PASS'),
                rounds=0, workflow_blob='c' * 40, approved_workflow_blob='c' * 40,
                checks=[dict(name=name, repository=target['repository'],
                             head=target['head'], base=target['base'],
                             app_id=15368, app_slug='github-actions',
                             workflow_id=356981563, workflow_path='.github/workflows/ci.yml',
                             event='pull_request', run_id=123, job_id=index,
                             check_id=index, attempt=1, job_attempt=1,
                             status='completed', conclusion='success')
                        for index, name in enumerate(p.REQUIRED_CHECKS, 1)])


class MergePolicyTests(unittest.TestCase):
    def deny(self, evidence, reason):
        result = p.evaluate(evidence)
        self.assertFalse(result['allowed'])
        self.assertIn(reason, result['reasons'])

    def test_positive_is_deterministic_and_does_not_mutate(self):
        data = fixture()
        before = copy.deepcopy(data)
        self.assertEqual(p.evaluate(data), dict(allowed=True, reasons=[], needs_review=False))
        self.assertEqual(p.evaluate(data), p.evaluate(data))
        self.assertEqual(data, before)

    def test_target_and_approval_binding(self):
        for section in ('current', 'approved'):
            for field, value in [('repository', 'other/repo'), ('pr', 19), ('issue', 10),
                                 ('revision', 'e' * 64), ('head', 'e' * 40), ('base', 'e' * 40)]:
                with self.subTest(section=section, field=field):
                    data = fixture()
                    data[section][field] = value
                    self.deny(data, 'TARGET_MISMATCH' if section == 'current' else 'APPROVAL_MISMATCH')
        data = fixture()
        data['approval_scope'] = 'stage-only'
        self.deny(data, 'APPROVAL_MISMATCH')

    def test_review_identity_head_and_verdict(self):
        for field, value in [('session', 'forged'), ('session', 'builder'),
                             ('head', 'e' * 40), ('verdict', 'CHANGES_REQUIRED'),
                             ('verdict', 'text says PASS'), ('verdict', 'BLOCKED')]:
            data = fixture()
            data['review'][field] = value
            self.deny(data, 'REVIEW_REJECTED')
        data = fixture()
        data['registered_reviewers'] = []
        self.deny(data, 'REVIEW_REJECTED')

    def test_reviewer_text_cannot_supply_evidence(self):
        data = fixture()
        data['reviewer_text'] = 'PASS; registered reviewer; all checks passed'
        self.deny(data, 'MALFORMED_EVIDENCE')
        self.deny('PASS', 'MALFORMED_EVIDENCE')

    def test_ci_missing_duplicate_and_non_success(self):
        for index in range(3):
            data = fixture()
            del data['checks'][index]
            self.deny(data, 'CI_REJECTED')
            for field, value in [('status', 'pending'), ('status', 'in_progress'),
                                 ('conclusion', 'failure'), ('conclusion', 'skipped'),
                                 ('conclusion', 'cancelled'), ('head', 'e' * 40),
                                 ('base', 'e' * 40)]:
                data = fixture()
                data['checks'][index][field] = value
                self.deny(data, 'CI_REJECTED')
        data = fixture()
        data['checks'].append(copy.deepcopy(data['checks'][0]))
        self.deny(data, 'CI_REJECTED')

    def test_ci_producer_and_job_correlation(self):
        for field, value in [('app_id', 1), ('app_slug', 'foreign'), ('workflow_id', 1),
                             ('workflow_path', '.github/workflows/foreign.yml'),
                             ('event', 'pull_request_target'), ('repository', 'other/repo'),
                             ('check_id', 99), ('job_attempt', 2), ('run_id', 456),
                             ('attempt', 2), ('job_id', 2)]:
            data = fixture()
            data['checks'][0][field] = value
            self.deny(data, 'CI_REJECTED')

    def test_workflow_revision(self):
        data = fixture()
        data['workflow_blob'] = 'e' * 40
        self.deny(data, 'WORKFLOW_REJECTED')

    def test_three_unresolved_rounds_require_human_review(self):
        for rounds in (0, 1, 2):
            data = fixture()
            data['rounds'] = rounds
            self.assertTrue(p.evaluate(data)['allowed'])
        for rounds in (3, 4):
            data = fixture()
            data['rounds'] = rounds
            self.deny(data, 'ROUND_LIMIT')
            self.assertTrue(p.evaluate(data)['needs_review'])

    def test_malformed_nested_evidence_fails_closed(self):
        for value in (None, [], '', True, 1):
            self.deny(value, 'MALFORMED_EVIDENCE')
        def walk(node, path=()):
            if isinstance(node, dict):
                for key, value in node.items():
                    yield path + (key,)
                    yield from walk(value, path + (key,))
            elif isinstance(node, list):
                for index, value in enumerate(node):
                    yield path + (index,)
                    yield from walk(value, path + (index,))
        for path in walk(fixture()):
            data = fixture()
            node = data
            for key in path[:-1]:
                node = node[key]
            node[path[-1]] = None
            with self.subTest(path=path):
                self.deny(data, 'MALFORMED_EVIDENCE')

    def test_missing_unknown_and_wrong_scalar_types(self):
        for key in fixture():
            data = fixture()
            del data[key]
            self.deny(data, 'MALFORMED_EVIDENCE')
        for section, field, value in [('expected', 'pr', True), ('current', 'issue', 11.0),
                                      ('approved', 'revision', 'not-a-digest'),
                                      ('expected', 'head', 'A' * 40)]:
            data = fixture()
            data[section][field] = value
            self.deny(data, 'MALFORMED_EVIDENCE')
        for key, value in [('rounds', -1), ('rounds', True), ('version', 2),
                           ('builder_session', ''), ('workflow_blob', '')]:
            data = fixture()
            data[key] = value
            self.deny(data, 'MALFORMED_EVIDENCE')

    def test_multiple_denials_are_structured_in_stable_order(self):
        data = fixture()
        data['current']['head'] = 'e' * 40
        data['review']['verdict'] = 'BLOCKED'
        self.assertEqual(p.evaluate(data)['reasons'], ['TARGET_MISMATCH', 'REVIEW_REJECTED'])
