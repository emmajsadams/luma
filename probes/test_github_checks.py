"""Public API-shaped fixtures; no credentials or network in unit tests."""
import copy
import importlib.util
from pathlib import Path
import unittest

SHA = '7754a033166989ebb8bbabacb31df61952ad2b57'
RUN = 34791027944
REPO = 'emmajsadams/luma'

def fixture():
    run = dict(id=RUN, workflow_id=356981563, path='.github/workflows/ci.yml',
               head_sha=SHA, event='pull_request', status='completed', conclusion='success',
               run_attempt=1, repository={'full_name': REPO}, head_repository={'full_name': REPO})
    checks = [dict(id=id_, name=name, head_sha=SHA, status='completed', conclusion='success',
                   app={'id': 15368, 'slug': 'github-actions'},
                   details_url=f'https://github.com/{REPO}/actions/runs/{RUN}/job/{id_}')
              for id_, name in [(103815154149, 'browser'), (103815154241, 'quality')]]
    jobs = [dict(id=c['id'], name=c['name'], head_sha=SHA, status='completed',
                 conclusion='success', run_id=RUN, run_attempt=1) for c in checks]
    return dict(checks=checks, run=run, jobs=jobs)

class GithubChecksTest(unittest.TestCase):
    def test_check_names_require_actions_run_job_provenance(self):
        path = Path(__file__).with_name('github_checks.py')
        self.assertTrue(path.exists(), 'read-only GitHub check adapter missing')
        spec = importlib.util.spec_from_file_location('github_checks', path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        valid = fixture()
        self.assertEqual(len(module.normalize(SHA, **valid)), 2)
        cases = []
        for field, value in [('status', 'in_progress'), ('conclusion', 'failure'),
                             ('head_sha', 'b' * 40), ('app', {'id': 1, 'slug': 'foreign'})]:
            item = copy.deepcopy(valid)
            item['checks'][0][field] = value
            cases.append(item)
        for field, value in [('workflow_id', 1), ('path', '.github/workflows/foreign.yml'),
                             ('event', 'pull_request_target'), ('head_sha', 'b' * 40)]:
            item = copy.deepcopy(valid)
            item['run'][field] = value
            cases.append(item)
        item = copy.deepcopy(valid)
        item['jobs'][0]['id'] = 1
        cases.append(item)
        item = copy.deepcopy(valid)
        item['checks'].append(copy.deepcopy(item['checks'][0]))
        cases.append(item)
        for item in cases:
            with self.subTest(item=item):
                self.assertEqual(module.normalize(SHA, **item), [])
