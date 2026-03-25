from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta

from database.database import SessionLocal
from database.repository import (
    get_patient_by_phone,
    create_patient,
    get_hospitals_by_pincode,
    get_available_doctors,
    create_appointment,
    create_otp,
    get_valid_otp,
    increment_otp_attempts,
    delete_otp
)

ivr_bp = Blueprint("ivr", __name__)


# -----------------------------
# Helper: Get DB session
# -----------------------------
def get_db():
    return SessionLocal()


# -----------------------------
# Entry Point for IVR Call
# -----------------------------
@ivr_bp.route("/call", methods=["POST"])
def ivr_call():
    """
    Entry point when patient calls the IVR number
    """
    phone_number = request.form.get("From") or request.json.get("from")

    db = get_db()

    patient = get_patient_by_phone(db, phone_number)

    if patient:
        # Returning user
        response = {
            "message": f"Welcome back {patient.name}. Please enter your PIN code."
        }
    else:
        # New user
        response = {
            "message": (
                "Welcome to MedConnect. "
                "Press 1 to register using Aadhaar. "
                "Press 2 to register manually."
            )
        }

    db.close()
    return jsonify(response)


# -----------------------------
# Aadhaar OTP Request (Mock)
# -----------------------------
@ivr_bp.route("/aadhaar/otp", methods=["POST"])
def request_otp():
    phone_number = request.form.get("From")
    otp_code = "123456"  # MOCK OTP (replace later)
    expires_at = datetime.utcnow() + timedelta(minutes=5)

    db = get_db()
    create_otp(db, phone_number, otp_code, expires_at)
    db.close()

    return jsonify({"message": "OTP sent successfully"})


# -----------------------------
# Aadhaar OTP Verification (Mock)
# -----------------------------
@ivr_bp.route("/aadhaar/verify", methods=["POST"])
def verify_otp():
    phone_number = request.form.get("From")
    user_otp = request.form.get("Digits")

    db = get_db()
    otp = get_valid_otp(db, phone_number)

    if not otp:
        db.close()
        return jsonify({"error": "OTP expired or invalid"}), 400

    if otp.attempts >= 3:
        delete_otp(db, otp)
        db.close()
        return jsonify({"error": "OTP attempts exceeded"}), 403

    if otp.otp_code != user_otp:
        increment_otp_attempts(db, otp)
        db.close()
        return jsonify({"error": "Incorrect OTP"}), 400

    delete_otp(db, otp)
    db.close()

    return jsonify({"message": "OTP verified successfully"})


# -----------------------------
# Manual Registration
# -----------------------------
@ivr_bp.route("/register/manual", methods=["POST"])
def manual_registration():
    phone_number = request.form.get("From")
    name = request.form.get("name")
    age = int(request.form.get("age"))
    gender = request.form.get("gender")

    db = get_db()
    patient = create_patient(db, phone_number, name, age, gender)
    db.close()

    return jsonify({
        "message": "Registration successful",
        "patient_id": patient.id
    })


# -----------------------------
# Get Hospitals by PIN Code
# -----------------------------
@ivr_bp.route("/hospitals", methods=["POST"])
def list_hospitals():
    pincode = request.form.get("Digits")

    db = get_db()
    hospitals = get_hospitals_by_pincode(db, pincode)
    db.close()

    return jsonify({
        "hospitals": [
            {"id": h.id, "name": h.name}
            for h in hospitals
        ]
    })


# -----------------------------
# Get Available Doctors
# -----------------------------
@ivr_bp.route("/doctors", methods=["POST"])
def list_doctors():
    hospital_id = int(request.form.get("hospital_id"))

    db = get_db()
    doctors = get_available_doctors(db, hospital_id)
    db.close()

    return jsonify({
        "doctors": [
            {"id": d.id, "name": d.name, "department": d.department}
            for d in doctors
        ]
    })


# -----------------------------
# Book OPD Appointment
# -----------------------------
@ivr_bp.route("/book", methods=["POST"])
def book_opd():
    phone_number = request.form.get("From")
    doctor_id = int(request.form.get("doctor_id"))
    hospital_id = int(request.form.get("hospital_id"))

    appointment_time = datetime.utcnow() + timedelta(minutes=30)
    token_number = f"TOKEN-{datetime.utcnow().strftime('%H%M%S')}"

    db = get_db()
    patient = get_patient_by_phone(db, phone_number)

    if not patient:
        db.close()
        return jsonify({"error": "Patient not registered"}), 400

    appointment = create_appointment(
        db,
        patient.id,
        doctor_id,
        hospital_id,
        token_number,
        appointment_time
    )
    db.close()

    return jsonify({
        "message": "OPD booked successfully",
        "token": appointment.token_number,
        "time": appointment.appointment_time.isoformat()
    })
