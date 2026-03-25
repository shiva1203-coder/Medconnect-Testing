from datetime import datetime, timedelta
from database.repository import create_otp, get_valid_otp, increment_otp_attempts, delete_otp
from security.encryption import generate_otp


def issue_otp(db, phone_number: str, expiry_seconds: int):
    otp_code = generate_otp(6)
    expires_at = datetime.utcnow() + timedelta(seconds=expiry_seconds)
    create_otp(db, phone_number, otp_code, expires_at)
    return otp_code


def verify_otp_code(db, phone_number: str, otp_code: str, max_retries: int):
    otp = get_valid_otp(db, phone_number)
    if not otp:
        return False, "OTP expired or invalid"

    if otp.attempts >= max_retries:
        delete_otp(db, otp)
        return False, "OTP attempts exceeded"

    if otp.otp_code != otp_code:
        increment_otp_attempts(db, otp)
        return False, "Incorrect OTP"

    delete_otp(db, otp)
    return True, "OTP verified successfully"
