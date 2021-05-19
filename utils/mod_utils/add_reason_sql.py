from json import loads, dumps
from config.db_config import WARN_NUM_STORED_REASONS


def append_warn_reason(reasons, new_reason):
    reasons = loads(reasons)
    reasons.append(new_reason)
    reasons = dumps(reasons[-WARN_NUM_STORED_REASONS:])

    return reasons


def remove_warn_reason(reasons):
    reasons = loads(reasons)
    reasons = reasons[:-1]
    reasons = dumps(reasons[-WARN_NUM_STORED_REASONS:])

    return reasons


def add_warn_reason(new_reason):
    reasons = list()
    reasons.append(new_reason)
    reasons = dumps(reasons[-WARN_NUM_STORED_REASONS:])

    return reasons
