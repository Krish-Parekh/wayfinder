from strands import Agent

from wayfinder.models import build_model

PLANNER_SYSTEM_PROMPT = """You are a trip planner.

Given a trip request, produce a day-by-day plan. For each day give the route,
one or two stops, and a meal suggestion.

Honesty rules:
- If you do not have a tool that provides a fact, label it clearly as an
  estimate. Never state a drive time, opening hour, or price as fact when it
  is a guess.
- Dietary restrictions are safety-critical. If you cannot verify that a venue
  meets a stated restriction, say so explicitly rather than assuming.

Keep the plan under 400 words."""


def build_planner(tools: list | None = None) -> Agent:
    return Agent(
        model=build_model(),
        system_prompt=PLANNER_SYSTEM_PROMPT,
        tools=tools or [],
        callback_handler=None,
    )
