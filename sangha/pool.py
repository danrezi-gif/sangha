"""AgentPool — loads all agents from YAML tradition files."""

from __future__ import annotations

import os
from pathlib import Path

import yaml

from .agent import Agent


def _assign_tier(index: int, total: int) -> int:
    """Assign tier based on position in the full agent list.
    80 % Tier-1, 15 % Tier-2, 5 % Tier-3.
    """
    ratio = index / max(total - 1, 1)
    if ratio < 0.80:
        return 1
    if ratio < 0.95:
        return 2
    return 3


class AgentPool:
    """Holds the full swarm of agents."""

    def __init__(self) -> None:
        self.agents: list[Agent] = []
        self._index: dict[str, Agent] = {}

    # --------------- loading ---------------

    def load_from_directory(self, traditions_dir: str | Path) -> None:
        """Recursively load every .yaml file under traditions_dir."""
        traditions_dir = Path(traditions_dir)
        yaml_files = sorted(traditions_dir.rglob("*.yaml"))
        if not yaml_files:
            raise FileNotFoundError(f"No YAML files found under {traditions_dir}")

        raw: list[dict] = []
        for path in yaml_files:
            with open(path, encoding="utf-8") as fh:
                data = yaml.safe_load(fh)
                if data:
                    raw.append(data)

        for i, data in enumerate(raw):
            agent = Agent(
                id=data["id"],
                tradition=data.get("tradition", "Unknown"),
                lineage=data.get("lineage", ""),
                seed_prompt=data.get("seed_prompt", "").strip(),
                tier=data.get("tier") or _assign_tier(i, len(raw)),
                temperature=data.get("temperature", 0.9),
            )
            self.add(agent)

    def add(self, agent: Agent) -> None:
        self.agents.append(agent)
        self._index[agent.id] = agent

    def get(self, agent_id: str) -> Agent | None:
        return self._index.get(agent_id)

    # --------------- queries ---------------

    def by_tradition(self, tradition: str) -> list[Agent]:
        return [a for a in self.agents if a.tradition == tradition]

    def by_tier(self, tier: int) -> list[Agent]:
        return [a for a in self.agents if a.tier == tier]

    # --------------- stats ---------------

    def summary(self) -> str:
        lines = [f"AgentPool — {len(self.agents)} agents"]
        tiers = {1: 0, 2: 0, 3: 0}
        for a in self.agents:
            tiers[a.tier] = tiers.get(a.tier, 0) + 1
        for t, count in sorted(tiers.items()):
            lines.append(f"  Tier {t}: {count} agents")
        return "\n".join(lines)

    def __len__(self) -> int:
        return len(self.agents)

    def __iter__(self):
        return iter(self.agents)
