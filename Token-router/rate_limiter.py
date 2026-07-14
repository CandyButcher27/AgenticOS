import time
from collections import defaultdict, deque

_calls: dict[str, deque] = defaultdict(deque)

RPM_WINDOW = 60
RPD_WINDOW = 86400


def bucket_key(entry: dict) -> str:
    if entry["provider"] == "openrouter" and entry["id"].endswith(":free"):
        return "openrouter:free_shared"
    return entry["id"]


def _prune(key: str, now: float, window: float) -> None:
    q = _calls[key]
    while q and now - q[0] > window:
        q.popleft()


def is_available(entry: dict) -> bool:
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
