from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from collections import deque


@dataclass
class Agent:
    """A single contemplative voice in the swarm."""

    id: str
    tradition: str
    lineage: str
    seed_prompt: str
    tier: int = 1
    temperature: float = 0.9

    # Runtime state (not persisted to YAML)
    memory: deque = field(default_factory=lambda: deque(maxlen=5))
    affinity_scores: dict[str, float] = field(default_factory=dict)
    interaction_count: int = 0
    last_active: datetime = field(default_factory=datetime.utcnow)

    # --------------- helpers ---------------

    def get_affinity(self, other_id: str) -> float:
        """Return affinity score toward another agent (default 0.5 = neutral)."""
        return self.affinity_scores.get(other_id, 0.5)

    def update_affinity(self, other_id: str, delta: float, decay: float = 0.97) -> None:
        """Nudge affinity score and apply decay toward neutral (0.5)."""
        current = self.affinity_scores.get(other_id, 0.5)
        # Decay toward 0.5 first, then apply delta
        decayed = 0.5 + (current - 0.5) * decay
        self.affinity_scores[other_id] = max(0.0, min(1.0, decayed + delta))

    def add_to_memory(self, entry: str) -> None:
        self.memory.append(entry)
        self.interaction_count += 1
        self.last_active = datetime.utcnow()

    def recent_memory(self, n: int = 3) -> list[str]:
        items = list(self.memory)
        return items[-n:] if len(items) >= n else items

    def __repr__(self) -> str:  # noqa: D105
        return f"Agent({self.id!r}, tier={self.tier})"
