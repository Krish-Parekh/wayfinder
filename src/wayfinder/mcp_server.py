from mcp.server.fastmcp import FastMCP

from wayfinder.config import settings
from wayfinder.geocoding import geocode
from wayfinder.routing import route
from wayfinder.types import BBox
from wayfinder.venues import find_venues
from wayfinder.weather import forecast

mcp = FastMCP("wayfinder-tools", host=settings.mcp_host, port=settings.mcp_port)


@mcp.tool()
def geocode_place(query: str) -> dict:
    """Resolve a place name to coordinates and a bounding box.

    Use this before any tool that needs coordinates. Accepts free text such as
    "Albury, NSW" or "Grampians National Park". Returns name, lat, lon and a
    bounding box with south/west/north/east edges.
    """
    return geocode(query).model_dump()


@mcp.tool()
def driving_route(waypoints: list[str]) -> dict:
    """Compute real driving distance and time through named waypoints, in order.

    Requires at least two waypoints. Returns per-leg distance in kilometres and
    duration in hours, plus totals. These are real road-network figures — use
    them instead of estimating drive times.
    """
    return route(waypoints).model_dump()


@mcp.tool()
def find_venues_near(
    south: float,
    west: float,
    north: float,
    east: float,
    amenity: str = "restaurant",
    diet: str | None = None,
    limit: int = 20,
) -> list[dict]:
    """Find venues inside a bounding box, optionally filtered by dietary tag.

    amenity accepts OpenStreetMap amenity values such as "restaurant", "cafe",
    "fast_food", "attraction", "museum". diet accepts exactly one of:
    vegetarian, vegan, gluten_free, halal, kosher.

    Each result carries a "source" field naming the OpenStreetMap element the
    data came from. Cite it when making a dietary claim. Absence of a dietary
    tag means the data is missing, NOT that the venue fails the requirement —
    never report an untagged venue as safe for an allergy.
    """
    bbox = BBox(south=south, west=west, north=north, east=east)
    return [
        v.model_dump()
        for v in find_venues(bbox, amenity=amenity, diet=diet, limit=limit)
    ]


@mcp.tool()
def daily_forecast(lat: float, lon: float, days: int = 7) -> list[dict]:
    """Get the daily forecast for a location: max temperature and rainfall.

    days must be between 1 and 16. Use this to decide whether outdoor stops are
    sensible on a given day.
    """
    return [d.model_dump() for d in forecast(lat, lon, days=days)]


def main() -> None:
    mcp.run(transport="streamable-http")


if __name__ == "__main__":
    main()
