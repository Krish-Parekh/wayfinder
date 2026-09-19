"""Create the AgentCore Memory resource once and print its id for .env.

    uv run python scripts/create_memory.py
"""

from bedrock_agentcore.memory import MemoryClient
from bedrock_agentcore.memory.constants import StrategyType

from wayfinder.config import settings

NAMESPACE = "/traveller/{actorId}/"

client = MemoryClient(region_name=settings.region)
memory = client.create_memory_and_wait(
    name="wayfinder",
    description="Traveller profiles: diet, allergies, companions, driving limits",
    strategies=[
        {StrategyType.USER_PREFERENCE.value: {"name": "preferences", "namespaces": [NAMESPACE]}},
        {StrategyType.SEMANTIC.value: {"name": "facts", "namespaces": [NAMESPACE]}},
    ],
    event_expiry_days=30,
)
print(f"MEMORY_ID={memory['id']}")
