from wayfinder.http import CachedClient
from wayfinder.types import DailyForecast

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"


def forecast(
    lat: float,
    lon: float,
    *,
    days: int = 7,
    client: CachedClient | None = None,
) -> list[DailyForecast]:
    if not 1 <= days <= 16:
        raise ValueError(f"days must be between 1 and 16, got {days}")

    client = client or CachedClient()
    payload = client.get_json(
        OPEN_METEO_URL,
        params={
            "latitude": lat,
            "longitude": lon,
            "daily": "temperature_2m_max,precipitation_sum",
            "timezone": "Australia/Sydney",
            "forecast_days": days,
        },
    )

    daily = payload["daily"]
    return [
        DailyForecast(date=date, temp_max_c=temp, precipitation_mm=rain)
        for date, temp, rain in zip(
            daily["time"],
            daily["temperature_2m_max"],
            daily["precipitation_sum"],
            strict=True,
        )
    ]
