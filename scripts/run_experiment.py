"""Main entry point for a Sangha experiment run."""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

import yaml
from dotenv import load_dotenv

# Allow running as `python scripts/run_experiment.py`
sys.path.insert(0, str(Path(__file__).parent.parent))

from sangha.db import Database
from sangha.engine import Engine
from sangha.pool import AgentPool

load_dotenv()


def load_settings() -> dict:
    cfg_path = Path("config/settings.yaml")
    if not cfg_path.exists():
        return {}
    with open(cfg_path) as fh:
        raw = yaml.safe_load(fh) or {}
    # Flatten swarm + memory sections for easy access
    flat = {}
    for section in ("swarm", "memory", "pairing", "emergence", "logging", "dashboard"):
        flat.update(raw.get(section, {}))
    return flat


async def main():
    settings = load_settings()

    # -- Agent Pool -------------------------------------------------------
    traditions_dir = Path("traditions")
    pool = AgentPool()
    pool.load_from_directory(traditions_dir)

    if len(pool) == 0:
        print("No agents found. Add tradition YAML files under traditions/")
        return

    # -- Database ---------------------------------------------------------
    db_path = settings.get("database", "data/sangha.db")
    db = Database(db_path)
    await db.connect()

    # -- Optional dashboard -----------------------------------------------
    on_event = None
    if settings.get("enabled", False):  # dashboard.enabled
        from dashboard.app import broadcast
        on_event = lambda ev: asyncio.create_task(broadcast(ev))

        import uvicorn
        from dashboard.app import app
        config = uvicorn.Config(
            app,
            host=settings.get("host", "127.0.0.1"),
            port=settings.get("port", 8765),
            log_level="warning",
        )
        server = uvicorn.Server(config)
        asyncio.create_task(server.serve())

    # -- Engine -----------------------------------------------------------
    engine = Engine(pool=pool, db=db, settings=settings, on_event=on_event)
    await engine.setup()

    cycles = settings.get("cycles_per_run", 50)
    await engine.run(num_cycles=cycles)

    await db.close()
    print(f"\nRun complete. Database saved to: {db_path}")


if __name__ == "__main__":
    asyncio.run(main())
