from wayfinder.http import CachedClient
from wayfinder.types import BBox, Place

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"


def geocode(query: str, *, client: CachedClient | None = None) -> Place:
    client = client or CachedClient()
    results = client.get_json(
        NOMINATIM_URL,
        params={"q": query, "format": "jsonv2", "limit": 1},
    )
    if not results:
        raise ValueError(f"No place found for {query!r}")

    hit = results[0]
    south, north, west, east = (float(v) for v in hit["boundingbox"])
    return Place(
        name=hit["display_name"],
        lat=float(hit["lat"]),
        lon=float(hit["lon"]),
        bbox=BBox(south=south, west=west, north=north, east=east),
    )
