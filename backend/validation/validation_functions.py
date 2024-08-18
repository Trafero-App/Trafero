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

def is_valid_license_plate(license_plate: str):
    """Check if phone number has a valid form"""
    license_plate_regex_pattern = r"^[A-Z] \d{1,7}$"
    valid_license_plate = (re.match(license_plate_regex_pattern, license_plate) is not None)
    return valid_license_plate
