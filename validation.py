from pydantic import BaseModel, model_validator
from typing import Literal, List
import regex as re
def is_valid_password(password: str):
    """Check if password has correct form"""
    password_regex_pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$"
    is_valid_password = re.match(password_regex_pattern, password) is not None
    return is_valid_password

def is_valid_dob(dob: str):
    """Check if date of birth has correct form"""
    dob_regex_pattern = r"^\d{4}-\d{2}-\d{2}$"
    is_valid_dob = re.match(dob_regex_pattern, dob) is not None
    return is_valid_dob

def is_valid_name(name: str):
    """Check if name (first name or last name) has correct form"""
    name_regex_pattern = r"^[a-zA-Z]+([ '-][a-zA-Z]+)*$"
    is_valid_name = re.match(name_regex_pattern, name) is not None
    return is_valid_name


def is_valid_email(email: str):
    """Check if email has a valid form"""
    email_regex_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    valid_email = re.match(email_regex_pattern, email) is not None
    return valid_email


def is_valid_phone_number(phone_number: str):
    """Check if phone number has a valid form"""
    phone_number_regex_pattern = r"^\d{8}$"
    valid_phone_number = (re.match(phone_number_regex_pattern, phone_number) is not None)
    return valid_phone_number


class Point(BaseModel):
    longitude: float
    latitude: float

class Account_Info(BaseModel):
    account_type: Literal["passenger", "vehicle"]
    password: str
    first_name: str
    last_name: str
    date_of_birth: str
    phone_number: str | None = None
    email: str | None = None
    status: Literal["active", "unknown", "inactive", "unavailable", "waiting"] | None = None
    cur_route_id: int | None = None
    routes:list | None = None
    license_plate: str | None = None

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
            
        if values.account_type == "vehicle":
            if values.phone_number is None:
                raise ValueError("Please provide a valid phone number")
            if values.status is None or values.cur_route_id is None \
                or values.license_plate is None or values.routes is None:
                raise ValueError("Please include status, current route id, valid route ids, and license plate for vehicle accounts.")
            if values.routes is None:
                raise ValueError("Please provide a list of route ids that the vehicle corresponds to.")
            if values.cur_route_id not in values.routes:
                raise ValueError("The current route id provided is not in the list of valid ids for this vehicle.")

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

