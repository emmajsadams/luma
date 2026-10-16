"""Exercise the real CLI entrypoint with a patched read-only API boundary."""
import contextlib
import io
import json
from pathlib import Path
import runpy
import sys
import unittest
from unittest.mock import patch
from test_github_checks import fixture, SHA, RUN


class CliTest(unittest.TestCase):
    def test_cli_rejects_changed_workflow_before_successful_ci(self):
        data = fixture()
        seen = []
        def response(args, **kwargs):
            path = args[2]
            seen.append(path)
            if '/contents/' in path:
                return json.dumps(dict(type='file', path='.github/workflows/ci.yml',
                                       sha=('a' if 'ref=' + SHA in path else 'b') * 40))
            if '/check-runs' in path:
                return json.dumps(dict(total_count=2, check_runs=data['checks']))
            if '/jobs' in path:
                return json.dumps(dict(total_count=2, jobs=data['jobs']))
            return json.dumps(data['run'])
        output = io.StringIO()
        argv = ['github_checks.py', SHA, str(RUN), 'c' * 40]
        with patch.object(sys, 'argv', argv), patch('subprocess.check_output', side_effect=response), contextlib.redirect_stdout(output):
            runpy.run_path(str(Path(__file__).with_name('github_checks.py')), run_name='__main__')
        self.assertEqual(json.loads(output.getvalue()), dict(verdict='WORKFLOW_REJECTED', merge_callback_calls=0, merge_authorized=False))
        self.assertEqual(len(seen), 2)
        self.assertTrue(all('/contents/' in path for path in seen))
