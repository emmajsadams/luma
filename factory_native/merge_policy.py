"""Pure trusted-evidence eligibility policy, NOT authentication or a merger.

Only a future trusted adapter may construct this JSON-compatible schema. Reviewer
prose is not an input. No I/O, clocks, callbacks, credential access or side effects.
"""
import re
from typing import TypedDict

REQUIRED_CHECKS = ('quality', 'browser', 'factory-native')
REPOSITORY = 'emmajsadams/luma'


class Decision(TypedDict):
    allowed: bool
    reasons: list[str]
    needs_review: bool


def text(value):
    return type(value) is str and bool(value.strip())


def positive(value):
    return type(value) is int and value > 0


def digest(length):
    return lambda value: type(value) is str and re.fullmatch('[0-9a-f]{%d}' % length, value) is not None


TARGET = dict(repository=text, pr=positive, issue=positive, revision=digest(64),
              head=digest(40), base=digest(40))
CHECK = dict(name=text, repository=text, head=digest(40), base=digest(40),
             app_id=positive, app_slug=text, workflow_id=positive, workflow_path=text,
             event=text, run_id=positive, job_id=positive, check_id=positive,
             attempt=positive, job_attempt=positive, status=text, conclusion=text)
SCHEMA = dict(version=lambda v: type(v) is int and v == 1,
              expected=TARGET, current=TARGET, approved=TARGET, approval_scope=text,
              builder_session=text, registered_reviewers=[text],
              review=dict(session=text, head=digest(40), verdict=text),
              rounds=lambda v: type(v) is int and v >= 0,
              workflow_blob=digest(40), approved_workflow_blob=digest(40), checks=[CHECK])


def valid(value, schema):
    if isinstance(schema, dict):
        return (type(value) is dict and value.keys() == schema.keys()
                and all(valid(value[key], rule) for key, rule in schema.items()))
    if isinstance(schema, list):
        return type(value) is list and all(valid(item, schema[0]) for item in value)
    return schema(value)


def evaluate(evidence) -> Decision:
    """Return stable reason codes; allowed means policy-eligible, not authorized.

    rounds counts unresolved completed feedback rounds, not infrastructure retries.
    At three rounds this conservative policy always requires human intervention.
    """
    if not valid(evidence, SCHEMA):
        return Decision(allowed=False, reasons=['MALFORMED_EVIDENCE'], needs_review=False)
    e = evidence
    target = e['expected']
    reasons = []
    if target['repository'] != REPOSITORY or e['current'] != target:
        reasons.append('TARGET_MISMATCH')
    if e['approved'] != target or e['approval_scope'] != 'merge':
        reasons.append('APPROVAL_MISMATCH')
    review = e['review']
    if (review['session'] == e['builder_session']
            or review['session'] not in e['registered_reviewers']
            or review['head'] != target['head'] or review['verdict'] != 'PASS'):
        reasons.append('REVIEW_REJECTED')
    if e['workflow_blob'] != e['approved_workflow_blob']:
        reasons.append('WORKFLOW_REJECTED')
    checks = e['checks']
    producer = dict(repository=REPOSITORY, head=target['head'], base=target['base'],
                    app_id=15368, app_slug='github-actions', workflow_id=356981563,
                    workflow_path='.github/workflows/ci.yml', event='pull_request',
                    status='completed', conclusion='success')
    if (sorted(c['name'] for c in checks) != sorted(REQUIRED_CHECKS)
            or len({c['job_id'] for c in checks}) != len(checks)
            or len({(c['run_id'], c['attempt']) for c in checks}) != 1
            or any(any(c[key] != value for key, value in producer.items())
                   or c['job_id'] != c['check_id'] or c['attempt'] != c['job_attempt']
                   for c in checks)):
        reasons.append('CI_REJECTED')
    if e['rounds'] >= 3:
        reasons.append('ROUND_LIMIT')
    return Decision(allowed=not reasons, reasons=reasons, needs_review='ROUND_LIMIT' in reasons)
