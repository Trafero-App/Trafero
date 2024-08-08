from pydantic import BaseModel

class vehicle_location(BaseModel):
    vehicle_id: int
    longitude: float
    latitude: float

class Account_Info(BaseModel):
    account_type: str
    username: str
    password: str
    first_name: str
    last_name: str
    phone_number: str

class Account_DB_Entry(BaseModel):
    account_type: str
    username: str
    password_hash: str
    first_name: str
    last_name: str
    phone_number: str
