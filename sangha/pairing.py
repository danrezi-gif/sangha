"""Pair selection strategies for agent interactions."""

from __future__ import annotations

import random
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .pool import AgentPool
    from .agent import Agent


def _traditions_differ(a: "Agent", b: "Agent") -> bool:
    return a.tradition != b.tradition


def select_pairs(
    pool: "AgentPool",
    count: int,
    strategy_mix: dict[str, float] | None = None,
) -> list[tuple["Agent", "Agent"]]:
    """Return `count` (agent_a, agent_b) pairs using the configured strategy mix."""
    if strategy_mix is None:
        strategy_mix = {
            "affinity_weighted": 0.40,
            "tradition_crossing": 0.30,
            "random": 0.20,
            "anti_affinity": 0.10,
        }

    agents = list(pool.agents)
    if len(agents) < 2:
        return []

    pairs: list[tuple["Agent", "Agent"]] = []
    used_ids: set[frozenset] = set()
    attempts = 0
    max_attempts = count * 20

    strategies = list(strategy_mix.keys())
    weights = list(strategy_mix.values())

    while len(pairs) < count and attempts < max_attempts:
        attempts += 1
        strategy = random.choices(strategies, weights=weights, k=1)[0]
        pair = _pick_pair(agents, strategy)
        if pair is None:
            continue
        key = frozenset([pair[0].id, pair[1].id])
        if key not in used_ids:
            used_ids.add(key)
            pairs.append(pair)

    return pairs


def _pick_pair(agents: list["Agent"], strategy: str) -> tuple["Agent", "Agent"] | None:
    if len(agents) < 2:
        return None

    if strategy == "random":
        a, b = random.sample(agents, 2)
        return (a, b)

    elif strategy == "affinity_weighted":
        a = random.choice(agents)
        others = [x for x in agents if x.id != a.id]
        scores = [a.get_affinity(x.id) for x in others]
        total = sum(scores)
        if total == 0:
            b = random.choice(others)
        else:
            b = random.choices(others, weights=scores, k=1)[0]
        return (a, b)

    elif strategy == "anti_affinity":
        a = random.choice(agents)
        others = [x for x in agents if x.id != a.id]
        # Invert: low affinity → high weight
        scores = [1.0 - a.get_affinity(x.id) for x in others]
        total = sum(scores)
        if total == 0:
            b = random.choice(others)
        else:
            b = random.choices(others, weights=scores, k=1)[0]
        return (a, b)

    elif strategy == "tradition_crossing":
        cross = [(a, b) for i, a in enumerate(agents)
                 for b in agents[i+1:]
                 if _traditions_differ(a, b)]
        if not cross:
            return _pick_pair(agents, "random")
        return random.choice(cross)

    return None
