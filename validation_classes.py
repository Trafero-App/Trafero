from time import sleep
from pydantic import BaseModel, model_validator, ValidationError
from typing import Literal
class vehicle_location(BaseModel):
    longitude: float
    latitude: float

class Account_Info(BaseModel):
    account_type: Literal["passenger", "vehicle"]
    username: str
    password: str
    first_name: str
    last_name: str
    phone_number: str | None = None
    email: str | None = None
    status: str | None = None
    cur_route_id: int | None = None
    routes:list | None = None
    license_plate: str | None = None

    @model_validator(mode="before")
    def phone_or_email(cls, values):
        if values.get("phone_number") is None and values.get("email") is None:
            raise ValueError("Please include either phone_number or email.")
        if values.get("account_type") == "vehicle":
            if values.get("status") is None or values.get("cur_route_id") is None \
                or values.get("license_plate") is None or values.get("routes") is None:
                raise ValueError("Please include status, current route id, valid route ids, and license plate for vehicle accounts.")
            if values.get("routes") is None:
                raise ValueError("Please provide a list of route ids that the vehicle corresponds to.")
            if values.get("cur_route_id") not in values.get("routes"):
                raise ValueError("The current route id provided is not in the list of valid ids for this vehicle.")
        
        return values
    

class Account_DB_Entry(Account_Info):
    password_hash: str
    password: None = None
    
class Point(BaseModel):
    longitude: float
    latitude: float

class Review(BaseModel):
    reaction: bool
    complaint: str | None = None
