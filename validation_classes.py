from pydantic import BaseModel

class vehicle_location(BaseModel):
    id: int
    longitude: float
    latitude: float

class Point(BaseModel):
    longitude: float
    latitude: float