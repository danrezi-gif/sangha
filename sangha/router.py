"""LiteLLM routing logic — maps agent tiers to models."""

from __future__ import annotations

import os
from pathlib import Path

import litellm
import yaml

litellm.set_verbose = False
litellm.drop_params = True  # ignore extra params silently

_TIERS_PATH = Path(__file__).parent.parent / "config" / "tiers.yaml"

with open(_TIERS_PATH) as fh:
    _TIER_CONFIG: dict[int, dict] = {
        int(k): v for k, v in yaml.safe_load(fh)["tiers"].items()
    }

_cost_accumulator: float = 0.0


def get_cost_so_far() -> float:
    return round(_cost_accumulator, 6)


async def llm_call(prompt: str, tier: int) -> str:
    """Make an async LLM call for the given tier. Returns response text."""
    global _cost_accumulator

    cfg = _TIER_CONFIG.get(tier, _TIER_CONFIG[1])

    response = await litellm.acompletion(
        model=cfg["model"],
        messages=[{"role": "user", "content": prompt}],
        max_tokens=cfg["max_tokens"],
        temperature=cfg["temperature"],
    )

    text = response.choices[0].message.content or ""

    # Rough cost tracking
    usage = getattr(response, "usage", None)
    if usage:
        in_tokens = getattr(usage, "prompt_tokens", 0)
        out_tokens = getattr(usage, "completion_tokens", 0)
        cost = (
            in_tokens / 1000 * cfg["cost_per_1k_input"]
            + out_tokens / 1000 * cfg["cost_per_1k_output"]
        )
        _cost_accumulator += cost

    return text.strip()
