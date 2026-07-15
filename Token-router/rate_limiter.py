'''
THis file ensures that we are thorough with the rate limiting part of things, it ensures that we are not unnescessarily 
wasting calls on prompts which we know are going to fail
'''
import json
import os
import time
from collections import defaultdict, deque

_calls: dict[str, deque] = defaultdict(deque)

RPM_WINDOW = 60
RPD_WINDOW = 86400
STATE_FILE = os.path.join(os.path.dirname(__file__), "rate_limiter_state.json")
_UNDER_PYTEST = "PYTEST_CURRENT_TEST" in os.environ


def _load_state() -> None:
    if not os.path.exists(STATE_FILE):
        return
    try:
        with open(STATE_FILE) as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return
    now = time.time()
    for key, timestamps in data.items():
        _calls[key] = deque(t for t in timestamps if now - t <= RPD_WINDOW)


def _save_state() -> None:
    data = {key: list(q) for key, q in _calls.items() if q}
    try:
        with open(STATE_FILE, "w") as f:
            json.dump(data, f)
    except OSError:
        pass


if not _UNDER_PYTEST:
    _load_state()


def bucket_key(entry: dict) -> str:
    if entry["provider"] == "openrouter" and entry["id"].endswith(":free"):
        return "openrouter:free_shared"
    return entry["id"]


def _prune(key: str, now: float, window: float) -> None:
    q = _calls[key]
    while q and now - q[0] > window:
        q.popleft()


def is_available(entry: dict) -> bool:
    '''
    This is the main function of the rate limiter it checks for the prd and prm while also ensuring that for the openrouter
    key we are merging all of the rate limits, and also that we have the largest window before we even touch pruning
    '''
    limits = entry.get("rate_limits") or {}
    rpm, rpd = limits.get("rpm"), limits.get("rpd")
    if rpm is None and rpd is None:
        return True

    key = bucket_key(entry)
    now = time.time()
    widest_window = max(w for w, limit in ((RPM_WINDOW, rpm), (RPD_WINDOW, rpd)) if limit is not None)
    _prune(key, now, widest_window)
    q = _calls[key]

    if rpm is not None and sum(1 for t in q if now - t <= RPM_WINDOW) >= rpm:
        return False
    if rpd is not None and sum(1 for t in q if now - t <= RPD_WINDOW) >= rpd:
        return False
    return True


def record_call(entry: dict) -> None:
    _calls[bucket_key(entry)].append(time.time())
    if not _UNDER_PYTEST:
        _save_state()
