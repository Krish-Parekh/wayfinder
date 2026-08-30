"""trip-orchestrator: parallel delegation over A2A, then composition.

Fan-out is an explicit asyncio.gather rather than exposing the specialists as
tools on an LLM. Tool-choice delegation lets the model decide the order and
whether to call each specialist at all, which is neither parallel nor
reproducible. The spec requires specialists to run in parallel, so the
parallelism lives in code.

Each delegation logs its start and finish with elapsed time. Three "-> " lines
appearing before any "<- " line is the observable proof of the fan-out.
"""

import asyncio
import logging
import time

from strands import Agent
from strands.agent.a2a_agent import A2AAgent

from wayfinder.config import settings
from wayfinder.models import build_model

logger = logging.getLogger("wayfinder.orchestrator")

SPECIALISTS: dict[str, str] = {
    "route-planner": f"http://127.0.0.1:{settings.route_planner_port}",
    "places-researcher": f"http://127.0.0.1:{settings.places_researcher_port}",
    "food-scout": f"http://127.0.0.1:{settings.food_scout_port}",
}

COMPOSER_SYSTEM_PROMPT = """You compose a final trip plan from specialist reports.

You will be given the traveller's original request and three reports:
route-planner (driving legs), places-researcher (stops), food-scout (meals).

Compose a day-by-day plan that uses all three. Rules:
- Do not invent facts. If no report mentions something, leave it out.
- Preserve every source citation and every safety caveat from food-scout
  verbatim. Never summarise an allergy warning away.
- If a report says a specialist was unavailable, say plainly which part of the
  plan is missing rather than filling the gap yourself.
- If two reports conflict, say so and prefer the one with a cited source.

Format: one section per day, then a short "Caveats" section at the end."""


async def fan_out(
    request: str,
    endpoints: dict[str, str],
    *,
    client_factory=A2AAgent,
) -> dict[str, str]:
    """Send the request to every specialist concurrently.

    A failing specialist yields an "unavailable" note instead of aborting the
    plan — a partial trip plan is more useful than none, provided the gap is
    stated.
    """

    async def call(name: str, endpoint: str) -> tuple[str, str]:
        logger.info("-> %s", name)
        started = time.monotonic()
        agent = client_factory(endpoint=endpoint, name=name)
        try:
            result = await agent.invoke_async(request)
            logger.info("<- %s (%.1fs)", name, time.monotonic() - started)
            return name, str(result)
        except Exception as exc:  # noqa: BLE001 - degrade, don't crash
            logger.warning(
                "<- %s FAILED (%.1fs): %s", name, time.monotonic() - started, exc
            )
            return name, f"[{name} unavailable: {exc}]"

    pairs = await asyncio.gather(
        *(call(name, endpoint) for name, endpoint in endpoints.items())
    )
    return dict(pairs)


async def plan_trip(request: str, endpoints: dict[str, str] | None = None) -> str:
    """Delegate in parallel, then compose the reports into one plan."""
    reports = await fan_out(request, endpoints or SPECIALISTS)

    briefing = "\n\n".join(
        f"### {name}\n{report}" for name, report in sorted(reports.items())
    )
    composer = Agent(
        model=build_model(settings.orchestrator_model_id),
        system_prompt=COMPOSER_SYSTEM_PROMPT,
        callback_handler=None,
    )
    result = composer(
        f"Traveller request:\n{request}\n\nSpecialist reports:\n{briefing}"
    )
    return str(result)


if __name__ == "__main__":
    import sys

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    print(asyncio.run(plan_trip(sys.argv[1])))
