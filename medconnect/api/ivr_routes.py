from flask import Blueprint, request, jsonify, current_app

from database.database import SessionLocal
from database.repository import get_patient_by_phone, get_hospitals_by_pincode, get_available_doctors
from core.patient.registration import register_patient
from core.auth.otp import issue_otp, verify_otp_code
from core.appointment.booking import book_next_slot
from security.validators import is_valid_phone, is_valid_pincode
from security.rate_limit import rate_limit


ivr_bp = Blueprint("ivr", __name__)


def get_db():
    return SessionLocal()


def get_value(*keys):
    payload = request.get_json(silent=True) or {}
    for key in keys:
        val = request.form.get(key)
        if val is not None:
            return val
        if key in payload:
            return payload[key]
    return None


@ivr_bp.route("/call", methods=["POST"])
def ivr_call():
    phone_number = get_value("From", "from")
    if not is_valid_phone(phone_number):
        return jsonify({"error": "Invalid phone number"}), 400

    db = get_db()
    try:
        patient = get_patient_by_phone(db, phone_number)
        if patient:
            response = {"message": f"Welcome back {patient.name}. Please enter your PIN code."}
        else:
            response = {
                "message": (
                    "Welcome to MedConnect. "
                    "Press 1 to register using Aadhaar. "
                    "Press 2 to register manually."
                )
            }
        return jsonify(response)
    finally:
        db.close()


@ivr_bp.route("/aadhaar/otp", methods=["POST"])
@rate_limit(limit=5, window_seconds=60)
def request_otp():
    phone_number = get_value("From", "from")
    if not is_valid_phone(phone_number):
        return jsonify({"error": "Invalid phone number"}), 400

    db = get_db()
    try:
        otp = issue_otp(db, phone_number, current_app.config["OTP_EXPIRY_SECONDS"])
        response = {"message": "OTP sent successfully"}
        if current_app.config.get("DEBUG"):
            response["otp_debug"] = otp
        return jsonify(response)
    finally:
        db.close()


@ivr_bp.route("/aadhaar/verify", methods=["POST"])
def verify_otp():
    phone_number = get_value("From", "from")
    user_otp = get_value("Digits", "otp")

    if not is_valid_phone(phone_number):
        return jsonify({"error": "Invalid phone number"}), 400
    if not user_otp:
        return jsonify({"error": "OTP is required"}), 400

    db = get_db()
    try:
        ok, message = verify_otp_code(db, phone_number, user_otp, current_app.config["OTP_MAX_RETRIES"])
        if not ok:
            return jsonify({"error": message}), 400
        return jsonify({"message": message})
    finally:
        db.close()


@ivr_bp.route("/register/manual", methods=["POST"])
def manual_registration():
    phone_number = get_value("From", "from")
    name = get_value("name")
    age = get_value("age")
    gender = get_value("gender")

    try:
        age = int(age)
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid age"}), 400

    db = get_db()
    try:
        if get_patient_by_phone(db, phone_number):
            return jsonify({"error": "Patient already registered"}), 409

        patient = register_patient(db, phone_number, name, age, gender)
        return jsonify({"message": "Registration successful", "patient_id": patient.id})
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    finally:
        db.close()


@ivr_bp.route("/hospitals", methods=["POST"])
def list_hospitals():
    pincode = get_value("Digits", "pincode")
    if not is_valid_pincode(pincode):
        return jsonify({"error": "Invalid pincode"}), 400

    db = get_db()
    try:
        hospitals = get_hospitals_by_pincode(db, pincode)
        return jsonify({"hospitals": [{"id": h.id, "name": h.name} for h in hospitals]})
    finally:
        db.close()


@ivr_bp.route("/doctors", methods=["POST"])
def list_doctors():
    hospital_id = get_value("hospital_id")
    try:
        hospital_id = int(hospital_id)
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid hospital_id"}), 400

    db = get_db()
    try:
        doctors = get_available_doctors(db, hospital_id)
        return jsonify({
            "doctors": [{"id": d.id, "name": d.name, "department": d.department} for d in doctors]
        })
    finally:
        db.close()


@ivr_bp.route("/book", methods=["POST"])
def book_opd():
    phone_number = get_value("From", "from")
    doctor_id = get_value("doctor_id")
    hospital_id = get_value("hospital_id")

    try:
        doctor_id = int(doctor_id)
        hospital_id = int(hospital_id)
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid doctor_id or hospital_id"}), 400

    db = get_db()
    try:
        patient = get_patient_by_phone(db, phone_number)
        if not patient:
            return jsonify({"error": "Patient not registered"}), 400

        appointment = book_next_slot(db, patient.id, doctor_id, hospital_id)
        return jsonify({
            "message": "OPD booked successfully",
            "token": appointment.token_number,
            "time": appointment.appointment_time.isoformat(),
        })
    finally:
        db.close()
