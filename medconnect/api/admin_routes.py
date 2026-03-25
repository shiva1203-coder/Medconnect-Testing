import os
from functools import wraps
from flask import Blueprint, request, jsonify

from database.database import SessionLocal
from database.repository import (
    get_hospital_by_id,
    set_doctor_availability,
    get_appointments_for_doctor,
    complete_appointment,
)

admin_bp = Blueprint("admin", __name__)


def get_db():
    return SessionLocal()


def require_admin_key(fn):
    @wraps(fn)
    def wrapped(*args, **kwargs):
        expected = os.getenv("ADMIN_API_KEY")
        if expected:
            provided = request.headers.get("X-Admin-Key")
            if provided != expected:
                return jsonify({"error": "Unauthorized"}), 401
        return fn(*args, **kwargs)

    return wrapped


@admin_bp.route("/hospitals/<int:hospital_id>/doctors", methods=["GET"])
@require_admin_key
def list_hospital_doctors(hospital_id):
    db = get_db()
    try:
        hospital = get_hospital_by_id(db, hospital_id)

        if not hospital:
            return jsonify({"error": "Hospital not found"}), 404

        return jsonify(
            {
                "hospital": hospital.name,
                "doctors": [
                    {
                        "id": d.id,
                        "name": d.name,
                        "department": d.department,
                        "is_available": d.is_available,
                    }
                    for d in hospital.doctors
                ],
            }
        )
    finally:
        db.close()


@admin_bp.route("/doctors/<int:doctor_id>/availability", methods=["POST"])
@require_admin_key
def update_doctor_availability(doctor_id):
    data = request.get_json(silent=True) or {}
    is_available = bool(data.get("is_available", True))

    db = get_db()
    try:
        doctor = set_doctor_availability(db, doctor_id, is_available)
        if not doctor:
            return jsonify({"error": "Doctor not found"}), 404

        return jsonify(
            {
                "message": "Doctor availability updated",
                "doctor_id": doctor.id,
                "is_available": doctor.is_available,
            }
        )
    finally:
        db.close()


@admin_bp.route("/doctors/<int:doctor_id>/appointments", methods=["GET"])
@require_admin_key
def doctor_opd_queue(doctor_id):
    db = get_db()
    try:
        appointments = get_appointments_for_doctor(db, doctor_id)
        return jsonify(
            {
                "appointments": [
                    {
                        "appointment_id": a.id,
                        "patient_name": a.patient.name,
                        "token": a.token_number,
                        "time": a.appointment_time.isoformat(),
                    }
                    for a in appointments
                ]
            }
        )
    finally:
        db.close()


@admin_bp.route("/appointments/<int:appointment_id>/complete", methods=["POST"])
@require_admin_key
def finish_appointment(appointment_id):
    db = get_db()
    try:
        appointment = complete_appointment(db, appointment_id)
        if not appointment:
            return jsonify({"error": "Appointment not found"}), 404

        return jsonify(
            {
                "message": "Appointment marked as completed",
                "appointment_id": appointment.id,
                "completed_at": appointment.completed_at.isoformat(),
            }
        )
    finally:
        db.close()
