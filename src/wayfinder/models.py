from strands.models import BedrockModel

from wayfinder.config import settings


def build_model(
    model_id: str | None = None,
    *,
    region: str | None = None,
    temperature: float = 0.3,
) -> BedrockModel:
    return BedrockModel(
        model_id=model_id or settings.specialist_model_id,
        region_name=region or settings.region,
        temperature=temperature,
    )
