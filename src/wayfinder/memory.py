"""Traveller profile on Bedrock AgentCore Memory.

One event per plan run goes in (the request and the plan); AgentCore's
USER_PREFERENCE and SEMANTIC strategies extract durable facts from it in
the background. Before the next run we query those facts and hand them
to the specialists, so a traveller's constraints follow them across trips.
"""

import logging
import uuid

from bedrock_agentcore.memory import MemoryClient

from wayfinder.config import settings

logger = logging.getLogger("wayfinder.memory")


def _namespace(traveller: str) -> str:
    return f"/traveller/{traveller}/"


def _client() -> MemoryClient:
    return MemoryClient(region_name=settings.region)


def load_profile(traveller: str, query: str, *, top_k: int = 10) -> list[str]:
    """Facts already known about this traveller, most relevant to `query` first."""
    records = _client().retrieve_memories(
        memory_id=settings.memory_id,
        namespace=_namespace(traveller),
        query=query,
        top_k=top_k,
    )
    facts = [r["content"]["text"] for r in records if r.get("content", {}).get("text")]
    logger.info("memory: %d facts for %s", len(facts), traveller)
    return facts


def save_run(traveller: str, request: str, plan: str) -> None:
    """Record one plan run; extraction into long-term memory is asynchronous."""
    _client().create_event(
        memory_id=settings.memory_id,
        actor_id=traveller,
        session_id=str(uuid.uuid4()),
        messages=[(request, "USER"), (plan, "ASSISTANT")],
    )
    logger.info("memory: run saved for %s", traveller)


def brief(request: str, facts: list[str]) -> str:
    """Prepend known facts so specialists honour constraints the request omits."""
    if not facts:
        return request
    known = "\n".join(f"- {f}" for f in facts)
    return f"{request}\n\nKnown about this traveller from previous trips:\n{known}"
