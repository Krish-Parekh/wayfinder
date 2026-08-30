from wayfinder.http import CachedClient
from wayfinder.types import BBox, Venue

OVERPASS_URL = "https://overpass-api.de/api/interpreter"

DIET_KEYS = ("vegetarian", "vegan", "gluten_free", "halal", "kosher")


def build_query(bbox: BBox, *, amenity: str, diet: str | None, limit: int) -> str:
    if diet is not None and diet not in DIET_KEYS:
        raise ValueError(f"Unknown diet {diet!r}; expected one of {DIET_KEYS}")

    diet_filter = f'["diet:{diet}"~"yes|only"]' if diet else ""
    return (
        "[out:json][timeout:25];"
        f'nwr["amenity"="{amenity}"]{diet_filter}({bbox.as_overpass()});'
        f"out center {limit};"
    )


def find_venues(
    bbox: BBox,
    *,
    amenity: str = "restaurant",
    diet: str | None = None,
    limit: int = 20,
    client: CachedClient | None = None,
) -> list[Venue]:
    client = client or CachedClient()
    query = build_query(bbox, amenity=amenity, diet=diet, limit=limit)
    payload = client.post_form(OVERPASS_URL, data={"data": query})

    venues: list[Venue] = []
    for element in payload.get("elements", []):
        tags = element.get("tags", {})
        name = tags.get("name")
        if not name:
            continue

        centre = element.get("center", element)
        if "lat" not in centre or "lon" not in centre:
            continue

        venues.append(
            Venue(
                name=name,
                lat=float(centre["lat"]),
                lon=float(centre["lon"]),
                kind=tags.get("amenity", amenity),
                opening_hours=tags.get("opening_hours"),
                diet={k: tags[f"diet:{k}"] for k in DIET_KEYS if f"diet:{k}" in tags},
                source=f"OSM {element['type']}/{element['id']} via Overpass",
            )
        )
    return venues
