"""Read-only GitHub provenance probe. Never authorizes or executes a merge.

Pinned workflow identity is observed configuration, not proof its YAML is trusted.
"""
import json
import re
import subprocess

REPO = 'emmajsadams/luma'
WORKFLOW_ID = 356981563


def normalize(sha, *, checks, run, jobs):
    if (run.get('workflow_id') != WORKFLOW_ID
            or run.get('path') != '.github/workflows/ci.yml'
            or run.get('head_sha') != sha or run.get('event') != 'pull_request'
            or run.get('status') != 'completed' or run.get('conclusion') != 'success'
            or run.get('repository', {}).get('full_name') != REPO
            or run.get('head_repository', {}).get('full_name') != REPO):
        return []
    result = []
    for name in ('quality', 'browser'):
        selected = [c for c in checks if c.get('name') == name]
        if len(selected) != 1:
            return []
        check = selected[0]
        matching = [j for j in jobs if j.get('id') == check.get('id')]
        if len(matching) != 1:
            return []
        job = matching[0]
        expected_url = f"https://github.com/{REPO}/actions/runs/{run['id']}/job/{check['id']}"
        if (check.get('app', {}).get('id') != 15368
                or check.get('app', {}).get('slug') != 'github-actions'
                or check.get('details_url') != expected_url
                or job.get('run_id') != run['id']
                or job.get('run_attempt') != run.get('run_attempt')
                or job.get('name') != name):
            return []
        for record in (check, job):
            if (record.get('head_sha') != sha or record.get('status') != 'completed'
                    or record.get('conclusion') != 'success'):
                return []
        result.append(dict(name=name, head_sha=sha, conclusion='success'))
    return result


def api(path):
    return json.loads(subprocess.check_output(['gh', 'api', path], text=True, timeout=30))


def fetch(sha, run_id):
    if not re.fullmatch(r'[0-9a-f]{40}', sha) or not re.fullmatch(r'[0-9]+', str(run_id)):
        raise ValueError('literal full SHA and numeric run ID required')
    prefix = f'repos/{REPO}'
    checks = api(f'{prefix}/commits/{sha}/check-runs?per_page=100')
    run = api(f'{prefix}/actions/runs/{run_id}')
    jobs = api(f'{prefix}/actions/runs/{run_id}/jobs?per_page=100')
    # Fail closed on pagination, rather than silently accepting partial evidence.
    if (checks['total_count'] != len(checks['check_runs'])
            or jobs['total_count'] != len(jobs['jobs'])):
        return []
    return normalize(sha, checks=checks['check_runs'], run=run, jobs=jobs['jobs'])


def evaluate(sha, run_id, reviewed_sha, merge_callback):
    """Connect read-only evidence to the deny-only gate; no reviewer is trusted yet."""
    from head_gate import attempt
    try:
        checks = fetch(sha, run_id)
    except (subprocess.SubprocessError, OSError, ValueError):
        checks = []
    return attempt(sha, reviewed_sha, merge_callback, checks=checks)


def evaluate_revision(sha, run_id, reviewed_sha, merge_callback, approved_base):
    """Conservative head/base blob equality, not executed-workflow attestation.

    approved_base is an explicit caller trust input, not approval discovered here.
    A PR merge ref may supply a missing head workflow; deny rather than infer trust.
    """
    if not all(isinstance(ref, str) and re.fullmatch(r'[0-9a-f]{40}', ref)
               for ref in (sha, approved_base)):
        return 'WORKFLOW_REJECTED'
    path = '.github/workflows/ci.yml'
    try:
        base = api(f'repos/{REPO}/contents/{path}?ref={approved_base}')
        head = api(f'repos/{REPO}/contents/{path}?ref={sha}')
        for record in (base, head):
            if (not isinstance(record, dict) or record.get('type') != 'file'
                    or record.get('path') != path
                    or not isinstance(record.get('sha'), str)
                    or not re.fullmatch(r'[0-9a-f]{40}', record['sha'])):
                return 'WORKFLOW_REJECTED'
        if base['sha'] != head['sha']:
            return 'WORKFLOW_REJECTED'
    except (subprocess.SubprocessError, OSError, ValueError):
        return 'WORKFLOW_REJECTED'
    return evaluate(sha, run_id, reviewed_sha, merge_callback)


if __name__ == '__main__':
    import sys
    calls = []
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('sha')
    parser.add_argument('run_id')
    parser.add_argument('approved_base', help='Explicit trust input; not discovered approval')
    args = parser.parse_args()
    verdict = evaluate_revision(args.sha, args.run_id, args.sha,
                                lambda: calls.append('merge'), args.approved_base)
    print(json.dumps({'verdict': verdict, 'merge_callback_calls': len(calls),
                      'merge_authorized': False}, sort_keys=True))
