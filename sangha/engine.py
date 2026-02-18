"""Interaction engine — the heartbeat of the swarm."""

from __future__ import annotations

import asyncio
from typing import Callable

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from .agent import Agent
from .db import Database
from .emergence import EmergenceDetector
from .pairing import select_pairs
from .pool import AgentPool
from .prompts import format_interaction, format_opening
from .router import get_cost_so_far, llm_call
from .utils import get_poetic_time, is_silence, truncate

console = Console()


class Engine:
    """Orchestrates the full swarm interaction loop."""

    def __init__(
        self,
        pool: AgentPool,
        db: Database,
        settings: dict,
        on_event: Callable[[dict], None] | None = None,
    ) -> None:
        self.pool = pool
        self.db = db
        self.settings = settings
        self.on_event = on_event  # hook for dashboard WebSocket broadcast
        self._cycle = 0
        self._swarm_pulse = ""
        self._detector: EmergenceDetector | None = None

    # --------------- bootstrap ---------------

    async def setup(self) -> None:
        """Persist all agents and initialise subsystems."""
        for agent in self.pool:
            await self.db.upsert_agent(agent)

        seed_vocab = EmergenceDetector.build_seed_vocabulary(self.pool)
        self._detector = EmergenceDetector(self.db, seed_vocab)

        console.rule("[bold magenta]SANGHA[/bold magenta]")
        console.print(self.pool.summary())
        console.print(f"[dim]Loaded {len(self.pool)} agents. Beginning at {get_poetic_time()}.[/dim]")

    # --------------- main loop ---------------

    async def run(self, num_cycles: int | None = None) -> None:
        cfg = self.settings
        total = num_cycles or cfg.get("cycles_per_run", 50)
        pairs_per = cfg.get("pairs_per_cycle", 5)
        delay = cfg.get("cycle_delay_seconds", 0.5)
        pulse_freq = cfg.get("swarm_pulse_frequency", 20)
        emergence_freq = cfg.get("emergence_detection_interval", 25)

        for _ in range(total):
            self._cycle += 1
            await self._run_cycle(pairs_per)

            if self._cycle % pulse_freq == 0:
                await self._update_pulse()

            if self._cycle % emergence_freq == 0 and self._detector:
                events = await self._detector.run(self._cycle, self.pool)
                for ev in events:
                    self._print_emergence(ev)
                    if self.on_event:
                        self.on_event(ev)

            total_interactions = await self.db.interaction_count()
            console.print(
                f"[dim]Cycle {self._cycle}/{total} — "
                f"{total_interactions} total interactions — "
                f"cost so far: ${get_cost_so_far():.4f}[/dim]"
            )

            await asyncio.sleep(delay)

    # --------------- cycle internals ---------------

    async def _run_cycle(self, pairs_per_cycle: int) -> None:
        pairs = select_pairs(self.pool, count=pairs_per_cycle)

        tasks = [self._run_pair(a, b) for a, b in pairs]
        await asyncio.gather(*tasks)

    async def _run_pair(self, agent_a: Agent, agent_b: Agent) -> None:
        # Agent A speaks first (opening)
        shared = await self.db.get_shared_history(agent_a.id, agent_b.id, limit=2)
        opening_prompt = format_opening(agent_a, self._swarm_pulse)
        message_a = await llm_call(opening_prompt, tier=agent_a.tier)

        # Agent B responds
        response_prompt = format_interaction(
            speaking_agent=agent_b,
            other_agent=agent_a,
            other_message=message_a,
            shared_history=shared,
            swarm_pulse=self._swarm_pulse,
        )
        message_b = await llm_call(response_prompt, tier=agent_b.tier)

        # Persist
        await self.db.log_interaction(
            self._cycle, agent_a.id, agent_b.id, message_a, message_b
        )

        # Update in-memory state
        entry_a = f"→ {agent_b.id}: {truncate(message_b)}"
        entry_b = f"→ {agent_a.id}: {truncate(message_a)}"
        agent_a.add_to_memory(entry_a)
        agent_b.add_to_memory(entry_b)

        # Update affinities (simple: silence lowers, rich exchange raises)
        delta = -0.05 if is_silence(message_a) or is_silence(message_b) else 0.03
        agent_a.update_affinity(agent_b.id, delta)
        agent_b.update_affinity(agent_a.id, delta)
        await self.db.update_affinity(agent_a.id, agent_b.id, agent_a.get_affinity(agent_b.id))

        self._print_exchange(agent_a, agent_b, message_a, message_b)

    # --------------- pulse ---------------

    async def _update_pulse(self) -> None:
        recent = await self.db.get_recent_interactions(limit=50)
        if not recent:
            return
        # Simple frequency-based pulse: most common non-stopword words
        stop = {"the", "and", "a", "in", "of", "to", "is", "it", "you", "that",
                "for", "with", "on", "this", "but", "are", "not", "your", "my"}
        words: list[str] = []
        for row in recent:
            for field in ("message_a", "message_b"):
                words += [
                    w.lower() for w in (row.get(field) or "").split()
                    if len(w) > 3 and w.lower() not in stop
                ]
        from collections import Counter
        common = Counter(words).most_common(8)
        self._swarm_pulse = ", ".join(w for w, _ in common)
        await self.db.save_pulse(self._cycle, self._swarm_pulse)
        console.print(f"[bold cyan]Swarm pulse:[/bold cyan] {self._swarm_pulse}")

    # --------------- printing ---------------

    def _print_exchange(
        self, a: Agent, b: Agent, msg_a: str, msg_b: str
    ) -> None:
        silence_a = is_silence(msg_a)
        silence_b = is_silence(msg_b)

        text = Text()
        text.append(f"{a.id}", style="bold yellow")
        text.append(f" [{a.tradition}]\n", style="dim")
        text.append(msg_a if not silence_a else "[silence]", style="italic")
        text.append(f"\n\n{b.id}", style="bold green")
        text.append(f" [{b.tradition}]\n", style="dim")
        text.append(msg_b if not silence_b else "[silence]", style="italic")

        console.print(Panel(text, subtitle=f"cycle {self._cycle}", expand=False))

    def _print_emergence(self, event: dict) -> None:
        console.print(
            Panel(
                f"[bold magenta]EMERGENCE[/bold magenta] [{event['type']}]\n"
                f"{event['description']}\n"
                f"significance: {event.get('significance', 0):.2f}",
                border_style="magenta",
            )
        )
