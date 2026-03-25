from flask import Blueprint, request, jsonify, current_app

from database.database import SessionLocal
from database.repository import (
    get_patient_by_phone,
    get_hospitals_by_pincode,
    get_available_doctors,
)
from core.patient.registration import register_patient
from core.auth.otp import issue_otp, verify_otp_code
from core.appointment.booking import book_next_slot
from security.encryption import create_access_token, verify_access_token
from security.validators import is_valid_phone, is_valid_pincode
from security.rate_limit import rate_limit


mobile_bp = Blueprint("mobile", __name__)


def get_db():
    return SessionLocal()


def _json():
    return request.get_json(silent=True) or {}


def _auth_payload():
    token = request.headers.get("Authorization", "").replace("Bearer ", "").strip()
    if not token:
        return None
    return verify_access_token(token)


@mobile_bp.route("/auth/request-otp", methods=["POST"])
@rate_limit(limit=5, window_seconds=60)
def request_mobile_otp():
    payload = _json()
    phone_number = payload.get("phone_number")

    if not is_valid_phone(phone_number):
        return jsonify({"error": "Invalid phone number"}), 400

    db = get_db()
    try:
        otp_code = issue_otp(db, phone_number, current_app.config["OTP_EXPIRY_SECONDS"])
        # In production this should be sent via SMS provider.
        response = {"message": "OTP sent"}
        if current_app.config.get("DEBUG"):
            response["otp_debug"] = otp_code
        return jsonify(response)
    finally:
        db.close()


@mobile_bp.route("/auth/verify-otp", methods=["POST"])
def verify_mobile_otp():
    payload = _json()
    phone_number = payload.get("phone_number")
    otp_code = payload.get("otp")

    if not is_valid_phone(phone_number):
        return jsonify({"error": "Invalid phone number"}), 400
    if not otp_code:
        return jsonify({"error": "OTP is required"}), 400

    db = get_db()
    try:
        ok, message = verify_otp_code(db, phone_number, otp_code, current_app.config["OTP_MAX_RETRIES"])
        if not ok:
            return jsonify({"error": message}), 400

        patient = get_patient_by_phone(db, phone_number)
        is_new_user = patient is None
        token = create_access_token({"phone_number": phone_number})

        return jsonify({
            "message": message,
            "access_token": token,
            "is_new_user": is_new_user,
        })
    finally:
        db.close()


@mobile_bp.route("/patients/register", methods=["POST"])
def register_mobile_patient():
    payload = _json()
    auth = _auth_payload()
    if not auth:
        return jsonify({"error": "Unauthorized"}), 401

    phone_number = auth["phone_number"]

    db = get_db()
    try:
        existing = get_patient_by_phone(db, phone_number)
        if existing:
            return jsonify({"error": "Patient already registered"}), 409

        patient = register_patient(
            db,
            phone_number=phone_number,
            name=payload.get("name", "").strip(),
            age=payload.get("age"),
            gender=payload.get("gender", ""),
        )
        return jsonify({
            "patient_id": patient.id,
            "name": patient.name,
            "phone_number": patient.phone_number,
        }), 201
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    finally:
        db.close()


@mobile_bp.route("/hospitals", methods=["GET"])
def mobile_hospitals():
    pincode = request.args.get("pincode")
    if not is_valid_pincode(pincode):
        return jsonify({"error": "Invalid pincode"}), 400

    db = get_db()
    try:
        hospitals = get_hospitals_by_pincode(db, pincode)
        return jsonify({
            "hospitals": [
                {"id": h.id, "name": h.name, "address": h.address}
                for h in hospitals
            ]
        })
    finally:
        db.close()


@mobile_bp.route("/hospitals/<int:hospital_id>/doctors", methods=["GET"])
def mobile_doctors(hospital_id):
    db = get_db()
    try:
        doctors = get_available_doctors(db, hospital_id)
        return jsonify({
            "doctors": [
                {
                    "id": d.id,
                    "name": d.name,
                    "department": d.department,
                }
                for d in doctors
            ]
        })
    finally:
        db.close()


@mobile_bp.route("/appointments", methods=["POST"])
def mobile_book_appointment():
    auth = _auth_payload()
    if not auth:
        return jsonify({"error": "Unauthorized"}), 401

    payload = _json()
    doctor_id = payload.get("doctor_id")
    hospital_id = payload.get("hospital_id")

    if not isinstance(doctor_id, int) or not isinstance(hospital_id, int):
        return jsonify({"error": "doctor_id and hospital_id must be integers"}), 400

    db = get_db()
    try:
        patient = get_patient_by_phone(db, auth["phone_number"])
        if not patient:
            return jsonify({"error": "Patient not registered"}), 404

        appointment = book_next_slot(db, patient.id, doctor_id, hospital_id)
        return jsonify({
            "appointment_id": appointment.id,
            "token_number": appointment.token_number,
            "appointment_time": appointment.appointment_time.isoformat(),
            "status": appointment.status,
        }), 201
    finally:
        db.close()
