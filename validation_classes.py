from pydantic import BaseModel, model_validator, ValidationError
from typing import Literal
class vehicle_location(BaseModel):
    vehicle_id: int
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
    status: bool | None = None
    route_id: bool | None = None

    @model_validator(mode="before")
    def phone_or_email(cls, values):
        if values.get("phone_number") is None and values.get("email") is None:
            print("OK")
            raise ValueError("Please include either phone_number or email")
        else: print("NO")
        if values.get("account_type") == "vehicle":
            if values.get("status") is None or values.get("route_id") is None:
                raise ValueError("Please include both status and route_id for vehicle accounts")
        
        return values
    

class Account_DB_Entry(Account_Info):
    password_hash: str
    password: None = None
    
