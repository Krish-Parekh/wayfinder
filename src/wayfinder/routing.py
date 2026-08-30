from wayfinder.geocoding import geocode
from wayfinder.http import CachedClient
from wayfinder.types import Place, Route, RouteLeg

# BRouter, not OSRM: router.project-osrm.org now resolves to the FOSSGIS host
# that also serves valhalla1.openstreetmap.de, and that host is unreachable.
# BRouter is the remaining routing service that needs no API key.
BROUTER_URL = "https://brouter.de/brouter"


def _leg(origin: Place, destination: Place, client: CachedClient) -> tuple[float, float]:
    """Return (distance_km, duration_hours) for one pair of points.

    BRouter returns a single track for a multi-point request, so legs are
    fetched a pair at a time to keep per-day distances honest.
    """
    payload = client.get_json(
        BROUTER_URL,
        params={
            "lonlats": (
                f"{origin.lon},{origin.lat}|{destination.lon},{destination.lat}"
            ),
            "profile": "car-fast",
            "alternativeidx": 0,
            "format": "geojson",
        },
    )
    properties = payload["features"][0]["properties"]
    return (
        float(properties["track-length"]) / 1000,
        float(properties["total-time"]) / 3600,
    )


def route(waypoints: list[str], *, client: CachedClient | None = None) -> Route:
    if len(waypoints) < 2:
        raise ValueError("A route needs at least two waypoints")

    client = client or CachedClient()
    places = [geocode(name, client=client) for name in waypoints]

    legs: list[RouteLeg] = []
    for i, (origin, destination) in enumerate(zip(places, places[1:], strict=False)):
        try:
            distance_km, duration_hours = _leg(origin, destination, client)
        except ValueError as exc:
            # BRouter reports failures as plain text, which fails JSON parsing.
            raise ValueError(
                f"No route from {waypoints[i]!r} to {waypoints[i + 1]!r}: {exc}"
            ) from exc
        legs.append(
            RouteLeg(
                from_name=waypoints[i],
                to_name=waypoints[i + 1],
                distance_km=distance_km,
                duration_hours=duration_hours,
            )
        )

    return Route(
        legs=legs,
        total_distance_km=sum(leg.distance_km for leg in legs),
        total_duration_hours=sum(leg.duration_hours for leg in legs),
    )
