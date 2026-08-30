from pydantic import BaseModel, Field


class BBox(BaseModel):
    south: float
    west: float
    north: float
    east: float

    def as_overpass(self) -> str:
        return f"{self.south},{self.west},{self.north},{self.east}"


class Place(BaseModel):
    name: str
    lat: float
    lon: float
    bbox: BBox


class RouteLeg(BaseModel):
    from_name: str
    to_name: str
    distance_km: float
    duration_hours: float


class Route(BaseModel):
    legs: list[RouteLeg]
    total_distance_km: float
    total_duration_hours: float


class Venue(BaseModel):
    name: str
    lat: float
    lon: float
    kind: str
    opening_hours: str | None = None
    diet: dict[str, str] = Field(default_factory=dict)
    source: str


class DailyForecast(BaseModel):
    date: str
    temp_max_c: float
    precipitation_mm: float
