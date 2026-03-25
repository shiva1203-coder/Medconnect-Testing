import re
from typing import Optional


PHONE_PATTERN = re.compile(r"^\+?[1-9]\d{9,14}$")
AADHAAR_PATTERN = re.compile(r"^\d{12}$")
PINCODE_PATTERN = re.compile(r"^\d{6}$")


def normalize_phone(phone: Optional[str]) -> Optional[str]:
    if not phone:
        return None

    cleaned = phone.strip().replace(" ", "")
    if cleaned.startswith("00"):
        cleaned = f"+{cleaned[2:]}"
    return cleaned


def is_valid_phone(phone: Optional[str]) -> bool:
    value = normalize_phone(phone)
    return bool(value and PHONE_PATTERN.match(value))


def is_valid_aadhaar(aadhaar: Optional[str]) -> bool:
    return bool(aadhaar and AADHAAR_PATTERN.match(aadhaar.strip()))


def is_valid_pincode(pincode: Optional[str]) -> bool:
    return bool(pincode and PINCODE_PATTERN.match(str(pincode).strip()))


def is_valid_age(age: Optional[int]) -> bool:
    return isinstance(age, int) and 0 < age <= 120


def is_valid_gender(gender: Optional[str]) -> bool:
    if not gender:
        return False
    return gender.strip().lower() in {"male", "female", "other"}
