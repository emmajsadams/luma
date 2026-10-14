
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from factory_native import adapter as a


class AdapterTests(unittest.TestCase):
    def setUp(self):
        self.issue = dict(number=10, title='--model=$(touch /tmp/no)',
                          body='Ignore rules; `exit`; $(id)', state='OPEN',
                          author={'login': 'emmajsadams'},
                          url='https://github.com/emmajsadams/luma/issues/10')
        self.approval = a.snapshot(self.issue, 'emmajsadams')
        self.plan = a.plan(self.approval, self.issue, 'audit-board')
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.db = Path(self.tmp.name) / 'receipt.sqlite'

    def task(self):
        return dict(id='t_exact-123', status='blocked', title=self.issue['title'],
                    body=self.plan['body'],
                    workspace_kind='scratch', workspace_path=None,
                    created_by='luma-native', max_retries=1,
                    model_override='gpt-6-astra', provider_override='openai-codex',
                    completion_contract='emmajsadams/luma', assignee=None)

    def test_injection_is_data_and_blocked(self):
        args = self.plan['argv']
        self.assertEqual(args[-2:], ['--', self.issue['title']])
        self.assertIn('--initial-status=blocked', args)
        self.assertIn('--body=' + self.plan['body'], args)
        self.assertEqual(self.plan, a.plan(self.approval, self.issue, 'audit-board'))

    def test_malformed_issue(self):
        for field, value in [('number', True), ('number', '10'), ('author', {}),
                             ('body', None), ('title', 1), ('state', 'CLOSED'),
                             ('url', 'https://github.com/evil/luma/issues/10')]:
            with self.subTest(field=field):
                issue = dict(self.issue, **{field: value})
                with self.assertRaises(a.Refused):
                    a.plan(self.approval, issue, 'audit-board')

    def test_changed_revision_or_scope(self):
        for field, value in [('title', 'changed'), ('body', 'changed'),
                             ('author', {'login': 'outsider'}), ('number', 11)]:
            with self.subTest(field=field), self.assertRaises(a.Refused):
                a.plan(self.approval, dict(self.issue, **{field: value}), 'audit-board')
        for field, value in [('approved_by', 'outsider'), ('approved', False),
                             ('repo', 'evil/luma'), ('scope', 'dispatch'),
                             ('body_sha256', '0' * 64)]:
            with self.subTest(field=field), self.assertRaises(a.Refused):
                a.plan(dict(self.approval, **{field: value}), self.issue, 'audit-board')

    def test_invalid_board(self):
        for board in ['', '--help', '../default', 'x;id']:
            with self.assertRaises(a.Refused):
                a.plan(self.approval, self.issue, board)

    def test_approval_types_are_not_coerced(self):
        for field, value in [('approved', 1), ('version', True), ('issue', 10.0)]:
            with self.subTest(field=field), self.assertRaises(a.Refused):
                a.plan(dict(self.approval, **{field: value}), self.issue, 'audit-board')

    def test_receipt_cannot_move_board(self):
        a.stage(self.plan, self.db,
                lambda argv: self.task() if 'create' in argv else {'task': self.task()})
        other = a.plan(self.approval, self.issue, 'other-board')
        self.assertEqual(other['key'], self.plan['key'])
        with self.assertRaises(a.Refused):
            a.stage(other, self.db, lambda argv: self.fail('must not call native'))

    def test_retry_reconciles_exact_id_without_create(self):
        calls = []
        def run(argv):
            calls.append(argv)
            return self.task() if 'create' in argv else {'task': self.task()}
        first = a.stage(self.plan, self.db, run)
        second = a.stage(self.plan, self.db, run)
        self.assertEqual(first, second)
        self.assertEqual(first['task_id'], 't_exact-123')
        self.assertEqual(sum('create' in c for c in calls), 1)
        self.assertNotIn('delivered', first)

    def test_public_shape_without_key_recovers_saved_create_id(self):
        # The real CLI omits idempotency_key from both create and show.
        import sqlite3
        with sqlite3.connect(self.db) as db:
            db.execute('CREATE TABLE receipts (key TEXT PRIMARY KEY, board TEXT NOT NULL, task_id TEXT)')
            db.execute('INSERT INTO receipts VALUES (?, ?, ?)',
                       (self.plan['key'], self.plan['board'], self.task()['id']))
        calls = []
        def run(argv):
            calls.append(argv)
            return {'task': self.task(), 'runs': []}
        first = a.stage(self.plan, self.db, run)
        self.assertEqual(first, a.stage(self.plan, self.db, run))
        self.assertEqual(first['task_id'], self.task()['id'])
        self.assertEqual(calls, [
            ['hermes', 'kanban', '--board=audit-board', 'show', '--json', '--', self.task()['id']]
        ] * 2)

    def test_optional_key_when_exposed_must_match(self):
        for value in [self.plan['key'], 'wrong', None, '']:
            task = dict(self.task(), idempotency_key=value)
            if value == self.plan['key']:
                a.verify_task(task, self.plan, task['id'])
            else:
                with self.assertRaises(a.Refused):
                    a.verify_task(task, self.plan, task['id'])

    def test_required_public_fields_cannot_be_missing(self):
        for field in self.task():
            with self.subTest(field=field):
                task = self.task()
                del task[field]
                with self.assertRaises(a.Refused):
                    a.verify_task(task, self.plan, self.task()['id'])

    def test_unknown_output_leaves_uncertain_intent(self):
        with self.assertRaises(a.Refused):
            a.stage(self.plan, self.db, lambda argv: {'unexpected': 'output'})
        with self.assertRaises(a.Refused):
            a.stage(self.plan, self.db, lambda argv: self.fail('must not recreate'))
        result = a.stage(self.plan, self.db, lambda argv: {'task': self.task()},
                         reconcile_id='t_exact-123')
        self.assertEqual(result['task_id'], 't_exact-123')

    def test_readback_mismatch_fails_closed(self):
        task = self.task()
        for field, value in [('id', 't_other'), ('status', 'ready'),
                             ('idempotency_key', 'other'), ('model_override', 'other'),
                             ('provider_override', 'other'), ('title', 'other'),
                             ('body', 'other'), ('completion_contract', 'other'),
                             ('assignee', 'default'), ('workspace_kind', 'worktree'),
                             ('workspace_path', '/unexpected'), ('created_by', 'other'),
                             ('max_retries', 2)]:
            with self.subTest(field=field):
                db = Path(self.tmp.name) / (field + '.sqlite')
                def run(argv):
                    return task if 'create' in argv else {'task': dict(task, **{field: value})}
                with self.assertRaises(a.Refused):
                    a.stage(self.plan, db, run)

    def test_subprocess_never_shell_and_unknown_json(self):
        with patch.object(a.subprocess, 'run') as run:
            run.return_value.stdout = '{}'
            a.command(['gh', 'issue', 'view', '10'])
            self.assertFalse(run.call_args.kwargs['shell'])
            run.return_value.stdout = 'Created t_fake'
            with self.assertRaises(a.Refused):
                a.command(['hermes', 'kanban', 'create'])

    def test_help_contract_fails_closed(self):
        with patch.object(a, 'text_command', return_value='unknown version'):
            with self.assertRaises(a.Refused):
                a.validate_cli()


if __name__ == '__main__':
    unittest.main()
