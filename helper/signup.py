import json
import shutil

from validation import Account_Info


def get_account_info_from_form(form_data: dict):

    routes = form_data.get("routes")
    if routes is not None: routes = json.loads(routes)

    form_data["routes"] = routes
    account_info = Account_Info(**form_data)

    return account_info


def get_files(form_data: dict):

    drivers_license_file = form_data.get("drivers_license_file")
    vehicle_registration_file = form_data.get("vehicle_registration_file")
    return drivers_license_file, vehicle_registration_file


def save_files(form_data, drivers_license_file_path, vehicle_registration_file_path):
    drivers_license_uploaded_file, vehicle_registration_uploaded_file = get_files(form_data)
    with open(drivers_license_file_path, "wb") as drivers_license_file:
        shutil.copyfileobj(drivers_license_uploaded_file.file, drivers_license_file)

    with open(vehicle_registration_file_path, "wb") as vehicle_registration_file:
        shutil.copyfileobj(vehicle_registration_uploaded_file.file, vehicle_registration_file)
        