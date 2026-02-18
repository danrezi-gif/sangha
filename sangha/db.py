"""SQLite persistence layer using aiosqlite."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import aiosqlite


SCHEMA = """
CREATE TABLE IF NOT EXISTS agents (
    id TEXT PRIMARY KEY,
    tradition TEXT,
    lineage TEXT,
    tier INTEGER,
    seed_prompt TEXT,
    temperature REAL,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS interactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cycle INTEGER,
    agent_a_id TEXT,
    agent_b_id TEXT,
    message_a TEXT,
    message_b TEXT,
    timestamp TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (agent_a_id) REFERENCES agents(id),
    FOREIGN KEY (agent_b_id) REFERENCES agents(id)
);

CREATE TABLE IF NOT EXISTS affinities (
    agent_a_id TEXT,
    agent_b_id TEXT,
    score REAL DEFAULT 0.5,
    interaction_count INTEGER DEFAULT 0,
    last_updated TEXT,
    PRIMARY KEY (agent_a_id, agent_b_id)
);

CREATE TABLE IF NOT EXISTS emergence_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cycle INTEGER,
    event_type TEXT,
    description TEXT,
    agents_involved TEXT,
    significance REAL,
    timestamp TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS swarm_pulse (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cycle INTEGER,
    summary TEXT,
    timestamp TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_interactions_cycle ON interactions(cycle);
CREATE INDEX IF NOT EXISTS idx_interactions_agents ON interactions(agent_a_id, agent_b_id);
"""


class Database:
    def __init__(self, db_path: str | Path) -> None:
        self.db_path = str(db_path)
        self._conn: aiosqlite.Connection | None = None

    async def connect(self) -> None:
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._conn = await aiosqlite.connect(self.db_path)
        self._conn.row_factory = aiosqlite.Row
        await self._conn.executescript(SCHEMA)
        await self._conn.commit()

    async def close(self) -> None:
        if self._conn:
            await self._conn.close()

    # --------------- agents ---------------

    async def upsert_agent(self, agent) -> None:  # noqa: ANN001
        await self._conn.execute(
            """INSERT OR REPLACE INTO agents (id, tradition, lineage, tier, seed_prompt, temperature)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (agent.id, agent.tradition, agent.lineage, agent.tier,
             agent.seed_prompt, agent.temperature),
        )
        await self._conn.commit()

    # --------------- interactions ---------------

    async def log_interaction(
        self, cycle: int, agent_a_id: str, agent_b_id: str,
        message_a: str, message_b: str,
    ) -> None:
        await self._conn.execute(
            """INSERT INTO interactions (cycle, agent_a_id, agent_b_id, message_a, message_b)
               VALUES (?, ?, ?, ?, ?)""",
            (cycle, agent_a_id, agent_b_id, message_a, message_b),
        )
        await self._conn.commit()

    async def get_shared_history(
        self, agent_a_id: str, agent_b_id: str, limit: int = 3
    ) -> list[str]:
        cursor = await self._conn.execute(
            """SELECT message_a, message_b FROM interactions
               WHERE (agent_a_id=? AND agent_b_id=?) OR (agent_a_id=? AND agent_b_id=?)
               ORDER BY id DESC LIMIT ?""",
            (agent_a_id, agent_b_id, agent_b_id, agent_a_id, limit),
        )
        rows = await cursor.fetchall()
        snippets = []
        for row in reversed(rows):
            snippets.append(f"{agent_a_id}: {row['message_a'][:100]}")
            snippets.append(f"{agent_b_id}: {row['message_b'][:100]}")
        return snippets

    async def get_recent_interactions(self, limit: int = 200) -> list[dict]:
        cursor = await self._conn.execute(
            """SELECT * FROM interactions ORDER BY id DESC LIMIT ?""", (limit,)
        )
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]

    # --------------- affinities ---------------

    async def update_affinity(
        self, agent_a_id: str, agent_b_id: str, score: float
    ) -> None:
        await self._conn.execute(
            """INSERT INTO affinities (agent_a_id, agent_b_id, score, interaction_count, last_updated)
               VALUES (?, ?, ?, 1, ?)
               ON CONFLICT(agent_a_id, agent_b_id) DO UPDATE SET
                   score=excluded.score,
                   interaction_count=interaction_count+1,
                   last_updated=excluded.last_updated""",
            (agent_a_id, agent_b_id, score, datetime.utcnow().isoformat()),
        )
        await self._conn.commit()

    # --------------- emergence ---------------

    async def log_emergence(
        self, cycle: int, event_type: str, description: str,
        agents_involved: list[str], significance: float,
    ) -> None:
        await self._conn.execute(
            """INSERT INTO emergence_events (cycle, event_type, description, agents_involved, significance)
               VALUES (?, ?, ?, ?, ?)""",
            (cycle, event_type, description, json.dumps(agents_involved), significance),
        )
        await self._conn.commit()

    # --------------- swarm pulse ---------------

    async def save_pulse(self, cycle: int, summary: str) -> None:
        await self._conn.execute(
            "INSERT INTO swarm_pulse (cycle, summary) VALUES (?, ?)", (cycle, summary)
        )
        await self._conn.commit()

    async def get_latest_pulse(self) -> str:
        cursor = await self._conn.execute(
            "SELECT summary FROM swarm_pulse ORDER BY id DESC LIMIT 1"
        )
        row = await cursor.fetchone()
        return row["summary"] if row else ""

    # --------------- stats ---------------

    async def interaction_count(self) -> int:
        cursor = await self._conn.execute("SELECT COUNT(*) as n FROM interactions")
        row = await cursor.fetchone()
        return row["n"] if row else 0
