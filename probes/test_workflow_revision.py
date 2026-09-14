"""Deny changed/missing workflow before consuming otherwise green CI."""
import subprocess
import unittest
from unittest.mock import patch
import github_checks as gate

SHA = '7754a033166989ebb8bbabacb31df61952ad2b57'
BASE = '3a509189ed1d57064efdf0a2bfdc5de3b6ff8403'
BLOB = '0ead2ae935bcd4eb4e9a327b953523c0226bc7b3'

class WorkflowRevisionTest(unittest.TestCase):
    def test_unapproved_or_missing_workflow_denies_green_ci(self):
        self.assertTrue(hasattr(gate, 'evaluate_revision'), 'workflow revision rejection missing')
        good = {'type': 'file', 'path': '.github/workflows/ci.yml', 'sha': BLOB}
        for candidate in ({**good, 'sha': 'a' * 40}, {},
                          subprocess.CalledProcessError(1, ['gh', 'api'])):
            calls = []
            with self.subTest(candidate=candidate), patch.object(gate, 'api', side_effect=[good, candidate]), patch.object(gate, 'evaluate', return_value='REVIEW_REJECTED') as evaluate:
                self.assertEqual(gate.evaluate_revision(SHA, 34791027944, SHA, lambda: calls.append(1), BASE), 'WORKFLOW_REJECTED')
                evaluate.assert_not_called()
                self.assertEqual(calls, [])
        with patch.object(gate, 'api', side_effect=[good, good]), patch.object(gate, 'evaluate', return_value='REVIEW_REJECTED'):
            self.assertEqual(gate.evaluate_revision(SHA, 34791027944, SHA, lambda: None, BASE), 'REVIEW_REJECTED')
