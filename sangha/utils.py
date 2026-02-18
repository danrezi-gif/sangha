"""Miscellaneous helpers."""

from __future__ import annotations

import re
from datetime import datetime


_POETIC_HOURS = [
    (5, "before-dawn"),
    (8, "dawn"),
    (11, "morning"),
    (14, "midday"),
    (17, "afternoon"),
    (20, "dusk"),
    (23, "evening"),
    (24, "deep-night"),
]


def get_poetic_time() -> str:
    hour = datetime.now().hour
    for threshold, label in _POETIC_HOURS:
        if hour < threshold:
            return label
    return "deep-night"


def truncate(text: str, max_chars: int = 120) -> str:
    if len(text) <= max_chars:
        return text
    return text[:max_chars].rstrip() + "…"


def is_silence(text: str) -> bool:
    return bool(re.search(r"\[silence\]", text, re.IGNORECASE))
