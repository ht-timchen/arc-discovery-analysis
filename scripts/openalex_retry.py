"""
OpenAlex HTTP GET with retries for transient failures (timeouts, 429, 5xx).

OpenAlex may slow or close connections under load; this module backs off and
retries instead of failing immediately. See:
https://docs.openalex.org/how-to-use-the-api/rate-limits-and-authentication
"""

from __future__ import annotations

import json
import random
import socket
import time
import urllib.error
import urllib.request
from email.utils import parsedate_to_datetime
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Tuple


def _retry_after_seconds(exc: urllib.error.HTTPError) -> Optional[float]:
    """Parse Retry-After header (seconds or HTTP-date)."""
    raw = exc.headers.get("Retry-After")
    if not raw:
        return None
    raw = raw.strip()
    try:
        return max(1.0, float(raw))
    except ValueError:
        pass
    try:
        dt = parsedate_to_datetime(raw)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return max(1.0, (dt - datetime.now(timezone.utc)).total_seconds())
    except (TypeError, ValueError, OSError):
        return None


def _is_timeout(err: BaseException) -> bool:
    if isinstance(err, TimeoutError):
        return True
    if isinstance(err, socket.timeout):
        return True
    if isinstance(err, urllib.error.URLError):
        r = getattr(err, "reason", None)
        if isinstance(r, TimeoutError):
            return True
        if r is not None and "timed out" in str(r).lower():
            return True
    msg = str(err).lower()
    return "timed out" in msg or "timeout" in msg


def _sleep_with_jitter(seconds: float) -> None:
    """Slight jitter to avoid thundering herd."""
    jitter = 1.0 + random.random() * 0.15
    time.sleep(min(600.0, max(0.5, seconds * jitter)))


def fetch_openalex_json(
    url: str,
    *,
    user_agent: str,
    timeout: float = 60.0,
    max_retries: int = 8,
    backoff_base: float = 15.0,
    backoff_max: float = 300.0,
) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """
    GET JSON from OpenAlex; retry on timeout / 429 / 5xx.

    Returns (parsed_json, None) on success, (None, error_message) on failure.
    HTTP 404 is not retried.
    """
    last_err: Optional[str] = None

    for attempt in range(max_retries + 1):
        req = urllib.request.Request(url, headers={"User-Agent": user_agent})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                body = resp.read().decode("utf-8")
                return json.loads(body), None
        except urllib.error.HTTPError as e:
            last_err = f"HTTP {e.code}"
            if e.code == 404:
                return None, "404"
            ra = _retry_after_seconds(e)
            if e.code == 429 and ra is not None:
                _sleep_with_jitter(ra)
                continue
            if e.code == 429:
                wait = min(backoff_max, backoff_base * (2**attempt))
                _sleep_with_jitter(wait)
                continue
            if e.code in (500, 502, 503, 504):
                wait = min(backoff_max, 5.0 * (2**attempt))
                _sleep_with_jitter(wait)
                continue
            return None, last_err
        except urllib.error.URLError as e:
            last_err = str(e) or "URLError"
            if attempt >= max_retries:
                break
            wait = min(backoff_max, backoff_base * (2**attempt))
            _sleep_with_jitter(wait)
            continue
        except TimeoutError as e:
            last_err = str(e) or "TimeoutError"
            if attempt >= max_retries:
                break
            wait = min(backoff_max, backoff_base * (2**attempt))
            _sleep_with_jitter(wait)
            continue
        except OSError as e:
            last_err = str(e)
            if attempt >= max_retries:
                break
            if _is_timeout(e):
                wait = min(backoff_max, backoff_base * (2**attempt))
            else:
                wait = min(backoff_max, backoff_base * (1.5**attempt))
            _sleep_with_jitter(wait)
            continue
        except json.JSONDecodeError as e:
            return None, f"JSON: {e}"
        except Exception as e:
            last_err = str(e) or type(e).__name__
            if attempt >= max_retries:
                break
            wait = min(backoff_max, backoff_base * (2**attempt))
            _sleep_with_jitter(wait)
            continue

    return None, last_err or "max retries exceeded"
