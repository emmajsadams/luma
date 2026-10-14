"""One-shot, owner-approved GitHub revision -> blocked native task adapter."""
import argparse
import hashlib
import json
import re
import sqlite3
import subprocess
from pathlib import Path

REPO = 'emmajsadams/luma'
OWNER = 'emmajsadams'
SCOPE = 'stage-only: blocked native task; no dispatch, delivery, review or merge'


class Refused(RuntimeError):
    pass


def require(condition, message):
    if not condition:
        raise Refused(message)


def digest(value):
    return hashlib.sha256(value.encode('utf-8')).hexdigest()


def text_command(argv):
    try:
        return subprocess.run(argv, shell=False, check=True, capture_output=True,
                              text=True, timeout=60).stdout
    except (OSError, subprocess.SubprocessError):
        raise Refused('CLI failed; diagnostics suppressed; reconcile before retry') from None


def command(argv):
    try:
        return json.loads(text_command(argv))
    except ValueError:
        raise Refused('Unknown CLI JSON output; reconcile before retry') from None


def validate_issue(issue):
    require(isinstance(issue, dict), 'Malformed issue')
    number = issue.get('number')
    require(type(number) is int and number in (10, 11), 'Unapproved issue scope')
    require(issue.get('state') == 'OPEN', 'Issue is not open')
    require(issue.get('url') == f'https://github.com/{REPO}/issues/{number}',
            'Mismatched repository/issue')
    require(isinstance(issue.get('author'), dict)
            and issue['author'].get('login') == OWNER, 'Unapproved author')
    for field in ('title', 'body'):
        require(isinstance(issue.get(field), str) and '\x00' not in issue[field],
                'Malformed title/body')


def fetch(number):
    require(type(number) is int and number in (10, 11), 'Unapproved issue scope')
    issue = command(['gh', 'issue', 'view', str(number), '--repo', REPO,
                     '--json', 'number,title,body,author,state,url'])
    validate_issue(issue)
    require(issue['number'] == number, 'Mismatched fetched issue')
    return issue


def snapshot(issue, approved_by):
    validate_issue(issue)
    require(approved_by == OWNER, 'Explicit local owner approval required')
    return dict(version=1, repo=REPO, issue=issue['number'], author=OWNER,
                title_sha256=digest(issue['title']), body_sha256=digest(issue['body']),
                approved=True, approved_by=OWNER, scope=SCOPE)


def plan(approval, issue, board):
    validate_issue(issue)
    require(isinstance(approval, dict) and approval.get('approved') is True
            and type(approval.get('version')) is int
            and type(approval.get('issue')) is int, 'Malformed approval types')
    require(approval == snapshot(issue, OWNER), 'Unapproved or changed revision/scope')
    require(isinstance(board, str) and re.fullmatch(r'[a-z0-9][a-z0-9-]{0,62}', board),
            'Explicit valid board required')
    key = 'luma-native-v1-' + digest(json.dumps(approval, sort_keys=True, separators=(',', ':')))
    body = json.dumps({'scope': SCOPE, 'source': issue['url'], 'revision': approval,
                       'untrusted_issue_body': issue['body']}, sort_keys=True)
    argv = ['hermes', 'kanban', '--board=' + board, 'create', '--json',
            '--initial-status=blocked', '--idempotency-key=' + key,
            '--model=gpt-6-astra', '--provider=openai-codex',
            '--completion-contract=' + REPO, '--workspace=scratch',
            '--max-retries=1', '--max-runtime=480', '--created-by=luma-native',
            '--body=' + body, '--', issue['title']]
    return dict(key=key, board=board, body=body, title=issue['title'], argv=argv)


def validate_cli():
    contracts = [(['hermes', 'kanban', '--help'], ['--board']),
                 (['hermes', 'kanban', 'create', '--help'],
                  ['--json', '--initial-status {blocked,running}', '--idempotency-key',
                   '--model', '--provider', '--completion-contract', '--workspace',
                   '--max-retries', '--max-runtime', '--created-by', '--body']),
                 (['hermes', 'kanban', 'show', '--help'], ['--json', 'task_id'])]
    for argv, required in contracts:
        help_text = text_command(argv)
        require(all(flag in help_text for flag in required), 'Unsupported installed native CLI')


def task_id(task):
    require(isinstance(task, dict), 'Unknown native task output')
    value = task.get('id')
    require(isinstance(value, str) and re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,127}', value),
            'Unknown native task id')
    return value


def verify_task(task, planned, exact_id):
    require(task_id(task) == exact_id, 'Native task id changed')
    expected = dict(status='blocked', title=planned['title'], body=planned['body'],
                    workspace_kind='scratch', workspace_path=None,
                    created_by='luma-native', max_retries=1, model_override='gpt-6-astra',
                    provider_override='openai-codex', completion_contract=REPO, assignee=None)
    require(all(k in task and task[k] == v for k, v in expected.items()),
            'Native task mismatch or no longer blocked; manual audit required')
    # Public CLI task JSON may omit the native dedupe key. Identity is bound
    # by the durable receipt's board/exact ID and the full revision-bearing body.
    # An exposed key is additional evidence, never an assumed readback guarantee.
    if 'idempotency_key' in task:
        require(task['idempotency_key'] == planned['key'], 'Native idempotency key mismatch')


def stage(planned, receipt_path, run=command, reconcile_id=None):
    """Persist intent before create; uncertain creates require explicit ID recovery.

    The receipt DB is mandatory durable local state, NOT an orchestration queue.
    Never delete it to retry. Archived tasks are never automatically recreated.
    """
    with sqlite3.connect(receipt_path, timeout=10) as db:
        db.execute('CREATE TABLE IF NOT EXISTS receipts (key TEXT PRIMARY KEY, board TEXT NOT NULL, task_id TEXT)')
        db.execute('BEGIN IMMEDIATE')
        row = db.execute('SELECT board, task_id FROM receipts WHERE key=?', (planned['key'],)).fetchone()
        if row:
            require(row[0] == planned['board'], 'Revision already bound to another board')
            exact_id = row[1]
            require(exact_id is not None or reconcile_id is not None,
                    'Uncertain create: supply --reconcile-id after manual native inspection')
            if reconcile_id:
                require(exact_id is None or exact_id == reconcile_id, 'Receipt id mismatch')
                exact_id = reconcile_id
            db.commit()
        else:
            require(reconcile_id is None, 'No uncertain receipt to reconcile')
            db.execute('INSERT INTO receipts VALUES (?, ?, NULL)', (planned['key'], planned['board']))
            db.commit()
            created = run(planned['argv'])
            exact_id = task_id(created)
            # Save the exact returned ID even if later validation/readback fails.
            db.execute('UPDATE receipts SET task_id=? WHERE key=?', (exact_id, planned['key']))
            db.commit()
            verify_task(created, planned, exact_id)
        task_id({'id': exact_id})
        output = run(['hermes', 'kanban', '--board=' + planned['board'], 'show', '--json', '--', exact_id])
        require(isinstance(output, dict) and isinstance(output.get('task'), dict), 'Unknown show output')
        verify_task(output['task'], planned, exact_id)
        db.execute('UPDATE receipts SET task_id=? WHERE key=?', (exact_id, planned['key']))
        return dict(key=planned['key'], board=planned['board'], task_id=exact_id, status='staged-blocked')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='action', required=True)
    approve = sub.add_parser('snapshot', help='Explicit local owner approval; prints revision JSON')
    approve.add_argument('--issue', type=int, choices=(10, 11), required=True)
    approve.add_argument('--approve-owner', choices=(OWNER,), required=True)
    prepare = sub.add_parser('stage')
    prepare.add_argument('--approval', type=Path, required=True)
    prepare.add_argument('--board', required=True)
    mode = prepare.add_mutually_exclusive_group()
    mode.add_argument('--dry-run', action='store_true')
    mode.add_argument('--apply-stage-only', action='store_true')
    prepare.add_argument('--receipts', type=Path)
    prepare.add_argument('--reconcile-id')
    args = parser.parse_args()
    try:
        if args.action == 'snapshot':
            result = snapshot(fetch(args.issue), args.approve_owner)
        else:
            approval = json.loads(args.approval.read_text())
            require(isinstance(approval, dict), 'Malformed approval')
            planned = plan(approval, fetch(approval.get('issue')), args.board)
            validate_cli()
            if args.apply_stage_only:
                require(args.receipts is not None, '--receipts is required for apply')
                result = stage(planned, args.receipts, reconcile_id=args.reconcile_id)
            else:
                require(args.reconcile_id is None, 'Reconciliation requires stage-only apply')
                result = dict(mode='dry-run', **planned)
        print(json.dumps(result, indent=2, sort_keys=True))
    except (Refused, OSError, ValueError, sqlite3.Error) as exc:
        parser.exit(2, 'Refused: ' + str(exc) + '\n')


if __name__ == '__main__':
    main()
