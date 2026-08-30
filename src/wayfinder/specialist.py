from strands import Agent
from strands.multiagent.a2a import A2AServer

from wayfinder.models import build_model
from wayfinder.planner import mcp_client


def build_specialist(
    name: str,
    description: str,
    system_prompt: str,
    tools: list,
) -> Agent:
    return Agent(
        name=name,
        description=description,
        model=build_model(),
        system_prompt=system_prompt,
        tools=tools,
        callback_handler=None,
    )


def serve_specialist(
    name: str,
    description: str,
    system_prompt: str,
    port: int,
) -> None:
    client = mcp_client()
    with client:
        tools = client.list_tools_sync()

        def agent_factory(context_id: str) -> Agent:
            return build_specialist(name, description, system_prompt, tools)

        A2AServer(agent_factory=agent_factory, port=port).serve()
