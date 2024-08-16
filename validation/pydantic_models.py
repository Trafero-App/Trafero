from pydantic import BaseModel, model_validator
from typing import Literal, List

from .validation_functions import is_valid_dob, is_valid_name, is_valid_password, is_valid_email, is_valid_phone_number

class Point(BaseModel):
    longitude: float
    latitude: float

class Account_Info(BaseModel):
    account_type: Literal["passenger", "driver"]
    password: str
    first_name: str
    last_name: str
    date_of_birth: str
    phone_number: str | None = None
    email: str | None = None
    cur_route_id: int | None = None
    status: Literal["active", "unknown", "inactive", "unavailable", "waiting"] | None= None
    vehicle_type: Literal["van", "bus"] | None = None
    brand: str | None = None
    model: str | None = None
    license_plate: str | None = None
    vehicle_color: str | None = None
    routes: List[int] | None = None

    @model_validator(mode="after")
    def phone_or_email(cls, values):
        if not is_valid_dob(values.date_of_birth):
            raise ValueError("Date of birth must be in YYYY-MM-DD format")
        if not is_valid_name(values.first_name) or not is_valid_name(values.last_name):
            raise ValueError("Name must consist of only alphabetic characters, spaces, dashes, and apostrophes")
        print(values, '\n\n\n')
        if values.password is not None and not is_valid_password(values.password):
            raise ValueError("You password is invalid")
        if (values.email is not None and not is_valid_email(values.email)) or \
           (values.phone_number and not is_valid_phone_number(values.phone_number)):
             raise ValueError("Invalid email and/or phone number")
        

        if values.account_type == "passenger":
            if values.phone_number is None and values.email is None:
                raise ValueError("Please provide either a phone_number or an email.")
            
        if values.account_type == "driver":
            if values.phone_number is None: raise ValueError("Please provide a valid phone number")
            if values.cur_route_id is None: values.cur_route_id = values.routes[0]
            if values.status is None: values.status = "inactive"
            if values.vehicle_type is None: raise ValueError("Please specify the vehicle's type")
            if values.brand is None: raise ValueError("Please specify the vehicle's brand")
            if values.model is None: raise ValueError("Please specify the vehicle's model")
            if values.license_plate is None: raise ValueError("Please specify your license plate")
            if values.vehicle_color is None: raise ValueError("Please specify the vehicle's color")
            if values.routes in (None, []): raise ValueError("Please provide a non-empty list of routes")
        return values
    

class Account_DB_Entry(Account_Info):
    password_hash: str
    password: None = None
    
class Passenger_Review(BaseModel):
    reaction: Literal["thumbs_up", "thumbs_down"]
    complaints: List[str] | None = None
    vehicle_id: int

    @model_validator(mode="before")
    def validate_review(cls, values):
        if values.get("reaction") == False:
            if values.get("complaints") is None:
                raise ValueError("Please include a list of complaints for negative reviews.")

        return values

class Review_DB_Entry(Passenger_Review):
    passenger_id: int
    
class Saved_Location(Point):
    name: str
    icon: str

class Saved_Vehicle(BaseModel):
    vehicle_id: int
    nickname: str