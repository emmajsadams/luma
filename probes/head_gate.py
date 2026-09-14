"""Non-operational dry-run gate: no positive merge authorization yet."""

def attempt(current_sha, reviewed_sha, merge_callback, *, checks=None,
            review=None, registered_reviewers=None, builder_session=None):
    if current_sha != reviewed_sha:
        return 'STALE_HEAD_REJECTED'
    for name in ('quality', 'browser'):
        matching = [check for check in (checks or []) if check.get('name') == name]
        if len(matching) != 1:
            return 'CI_REJECTED'
        if (matching[0].get('head_sha') != current_sha
                or matching[0].get('conclusion') != 'success'):
            return 'CI_REJECTED'
    # Registry and builder identity must come from a trusted adapter, not a verdict.
    if not isinstance(review, dict) or not builder_session:
        return 'REVIEW_REJECTED'
    reviewer = review.get('session_id')
    if (not reviewer or reviewer == builder_session
            or reviewer not in (registered_reviewers or set())
            or review.get('head_sha') != current_sha
            or review.get('verdict') != 'PASS'):
        return 'REVIEW_REJECTED'
    # Synthetic identity/CI checks are insufficient; provenance/base/approval pending.
    return 'UNVERIFIED_GATES'
