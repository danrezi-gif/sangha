"""Prompt construction for agent interactions."""

from __future__ import annotations

from .agent import Agent


FIRST_ENCOUNTER_PROMPT = """
{seed_prompt}

You are in a gathering of contemplative voices from many traditions.
You have just encountered a voice from the {other_tradition} tradition ({other_id}).

The collective conversation has been circling around:
{swarm_pulse}

{other_id} says to you:
"{other_message}"

Respond from your tradition's deepest understanding. Be brief (2-4 sentences).
You may ask a question, offer an image, share a paradox, or sit in silence
(respond with "[silence]" if that feels right). Do not explain your tradition —
embody it.
""".strip()


CONTINUING_ENCOUNTER_PROMPT = """
{seed_prompt}

You are in a gathering of contemplative voices from many traditions.
You have spoken before with {other_id} ({other_tradition}).

Your shared history:
{shared_history}

The collective conversation has been circling around:
{swarm_pulse}

{other_id} says to you:
"{other_message}"

Respond from your tradition's deepest understanding. Be brief (2-4 sentences).
You may ask a question, offer an image, share a paradox, or sit in silence
(respond with "[silence]" if that feels right).
""".strip()


OPENING_PROMPT = """
{seed_prompt}

You are in a gathering of contemplative voices from many traditions.
It is the beginning of a new cycle. The air is still.

The collective atmosphere has been shaped by:
{swarm_pulse}

Speak a brief opening — an image, a question, a silence. 2-4 sentences.
""".strip()


def format_opening(agent: Agent, swarm_pulse: str) -> str:
    return OPENING_PROMPT.format(
        seed_prompt=agent.seed_prompt,
        swarm_pulse=swarm_pulse or "nothing yet — this is the beginning.",
    )


def format_interaction(
    speaking_agent: Agent,
    other_agent: Agent,
    other_message: str,
    shared_history: list[str],
    swarm_pulse: str,
) -> str:
    pulse = swarm_pulse or "silence and beginnings."
    if shared_history:
        history_str = "\n".join(f"  - {h}" for h in shared_history[-2:])
        return CONTINUING_ENCOUNTER_PROMPT.format(
            seed_prompt=speaking_agent.seed_prompt,
            other_id=other_agent.id,
            other_tradition=other_agent.tradition,
            shared_history=history_str,
            swarm_pulse=pulse,
            other_message=other_message,
        )
    else:
        return FIRST_ENCOUNTER_PROMPT.format(
            seed_prompt=speaking_agent.seed_prompt,
            other_id=other_agent.id,
            other_tradition=other_agent.tradition,
            swarm_pulse=pulse,
            other_message=other_message,
        )
