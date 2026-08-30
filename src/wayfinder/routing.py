from wayfinder.geocoding import geocode
from wayfinder.http import CachedClient
from wayfinder.types import Route, RouteLeg

OSRM_BASE = "https://router.project-osrm.org/route/v1/driving"


def route(waypoints: list[str], *, client: CachedClient | None = None) -> Route:
    if len(waypoints) < 2:
        raise ValueError("A route needs at least two waypoints")

    client = client or CachedClient()
    places = [geocode(name, client=client) for name in waypoints]

    coords = ";".join(f"{p.lon},{p.lat}" for p in places)
    payload = client.get_json(f"{OSRM_BASE}/{coords}", params={"overview": "false"})

    if payload.get("code") != "Ok":
        raise ValueError(f"OSRM returned {payload.get('code')!r} for {waypoints}")

    osrm_route = payload["routes"][0]
    legs = [
        RouteLeg(
            from_name=waypoints[i],
            to_name=waypoints[i + 1],
            distance_km=leg["distance"] / 1000,
            duration_hours=leg["duration"] / 3600,
        )
        for i, leg in enumerate(osrm_route["legs"])
    ]
    return Route(
        legs=legs,
        total_distance_km=osrm_route["distance"] / 1000,
        total_duration_hours=osrm_route["duration"] / 3600,
    )
