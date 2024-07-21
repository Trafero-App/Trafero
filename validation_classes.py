from pydantic import BaseModel

class vehicle_location(BaseModel):
    vehicle_id: int
    longitude: float
    latitude: float

class Point(BaseModel):
    longitude: float
    latitude: float