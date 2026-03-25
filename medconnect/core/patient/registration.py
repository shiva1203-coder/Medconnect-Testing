from database.repository import create_patient
from security.validators import is_valid_age, is_valid_gender, is_valid_phone


def register_patient(db, phone_number: str, name: str, age: int, gender: str):
    if not is_valid_phone(phone_number):
        raise ValueError("Invalid phone number")
    if not name or len(name.strip()) < 2:
        raise ValueError("Invalid name")
    if not is_valid_age(age):
        raise ValueError("Invalid age")
    if not is_valid_gender(gender):
        raise ValueError("Invalid gender")

    return create_patient(db, phone_number=phone_number, name=name.strip(), age=age, gender=gender.strip().title())
