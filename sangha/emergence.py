"""Emergence detection — the part that makes it art."""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

from .db import Database


class EmergenceDetector:
    """Monitors the swarm for interesting patterns and logs them."""

    def __init__(self, db: Database, seed_vocabulary: set[str] | None = None) -> None:
        self.db = db
        self._prev_phrase_counts: Counter = Counter()
        self.seed_vocabulary: set[str] = seed_vocabulary or set()
        self.journal_path = Path("data/emergence_journal.jsonl")
        self.journal_path.parent.mkdir(parents=True, exist_ok=True)

    # --------------- main entry point ---------------

    async def run(self, cycle: int, pool) -> list[dict]:  # noqa: ANN001
        """Run all detectors. Returns list of detected events."""
        events: list[dict] = []

        recent = await self.db.get_recent_interactions(limit=300)
        if not recent:
            return events

        # 1. Novel phrases
        novel_events = await self._detect_novel_phrases(cycle, recent)
        events.extend(novel_events)

        # 2. Silence patterns
        silence_event = await self._detect_silence(cycle, recent)
        if silence_event:
            events.append(silence_event)

        # 3. Log all events
        for ev in events:
            await self.db.log_emergence(
                cycle=ev["cycle"],
                event_type=ev["type"],
                description=ev["description"],
                agents_involved=ev.get("agents", []),
                significance=ev.get("significance", 0.5),
            )
            self._write_journal(ev)

        return events

    # --------------- detectors ---------------

    async def _detect_novel_phrases(
        self, cycle: int, recent: list[dict]
    ) -> list[dict]:
        text = " ".join(
            (r.get("message_a") or "") + " " + (r.get("message_b") or "")
            for r in recent
        )
        phrases = self._extract_bigrams(text)
        current_counts = Counter(phrases)

        novel: list[dict] = []
        for phrase, count in current_counts.items():
            # Appeared 3+ times and wasn't in seed vocabulary
            if count >= 3 and phrase not in self.seed_vocabulary:
                prev = self._prev_phrase_counts.get(phrase, 0)
                if prev < 3:  # Just crossed the threshold
                    novel.append({
                        "cycle": cycle,
                        "type": "novel_concept",
                        "description": (
                            f"Emergent phrase '{phrase}' appeared {count}x "
                            f"— not in any seed tradition."
                        ),
                        "agents": [],
                        "significance": min(1.0, count / 10),
                    })

        self._prev_phrase_counts = current_counts
        return novel

    async def _detect_silence(self, cycle: int, recent: list[dict]) -> dict | None:
        total = len(recent)
        silences = sum(
            1 for r in recent
            if "[silence]" in (r.get("message_a") or "").lower()
            or "[silence]" in (r.get("message_b") or "").lower()
        )
        ratio = silences / max(total, 1)
        if ratio > 0.15:
            return {
                "cycle": cycle,
                "type": "collective_silence",
                "description": (
                    f"Collective silence: {silences}/{total} recent exchanges "
                    f"({ratio:.0%}) contained [silence]."
                ),
                "agents": [],
                "significance": min(1.0, ratio * 3),
            }
        return None

    # --------------- helpers ---------------

    @staticmethod
    def _extract_bigrams(text: str) -> list[str]:
        words = re.findall(r"\b[a-z]{4,}\b", text.lower())
        return [f"{words[i]} {words[i+1]}" for i in range(len(words) - 1)]

    def _write_journal(self, event: dict) -> None:
        with open(self.journal_path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(event) + "\n")

    @classmethod
    def build_seed_vocabulary(cls, pool) -> set[str]:  # noqa: ANN001
        """Extract all bigrams from every agent's seed prompt."""
        combined = " ".join(a.seed_prompt for a in pool)
        return set(cls._extract_bigrams(combined))
