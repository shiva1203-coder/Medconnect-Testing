from flask import Blueprint, request, jsonify
from datetime import datetime

from database.database import SessionLocal
from database.repository import (
    get_hospital_by_id,
    get_available_doctors,
    set_doctor_availability,
    get_appointments_for_doctor,
    complete_appointment
)

admin_bp = Blueprint("admin", __name__)


# -----------------------------
# Helper: DB Session
# -----------------------------
def get_db():
    return SessionLocal()


# -----------------------------
# Get Doctors of a Hospital
# -----------------------------
@admin_bp.route("/hospitals/<int:hospital_id>/doctors", methods=["GET"])
def list_hospital_doctors(hospital_id):
    db = get_db()
    hospital = get_hospital_by_id(db, hospital_id)

    if not hospital:
        db.close()
        return jsonify({"error": "Hospital not found"}), 404

    doctors = hospital.doctors
    db.close()

    return jsonify({
        "hospital": hospital.name,
        "doctors": [
            {
                "id": d.id,
                "name": d.name,
                "department": d.department,
                "is_available": d.is_available
            }
            for d in doctors
        ]
    })


# -----------------------------
# Set Doctor Availability
# -----------------------------
@admin_bp.route("/doctors/<int:doctor_id>/availability", methods=["POST"])
def update_doctor_availability(doctor_id):
    is_available = request.json.get("is_available", True)

    db = get_db()
    doctor = set_doctor_availability(db, doctor_id, is_available)
    db.close()

    if not doctor:
        return jsonify({"error": "Doctor not found"}), 404

    return jsonify({
        "message": "Doctor availability updated",
        "doctor_id": doctor.id,
        "is_available": doctor.is_available
    })


# -----------------------------
# Doctor Dashboard: OPD Queue
# -----------------------------
@admin_bp.route("/doctors/<int:doctor_id>/appointments", methods=["GET"])
def doctor_opd_queue(doctor_id):
    db = get_db()
    appointments = get_appointments_for_doctor(db, doctor_id)
    db.close()

    return jsonify({
        "appointments": [
            {
                "appointment_id": a.id,
                "patient_name": a.patient.name,
                "token": a.token_number,
                "time": a.appointment_time.isoformat()
            }
            for a in appointments
        ]
    })


# -----------------------------
# Mark Consultation Finished
# -----------------------------
@admin_bp.route("/appointments/<int:appointment_id>/complete", methods=["POST"])
def finish_appointment(appointment_id):
    db = get_db()
    appointment = complete_appointment(db, appointment_id)
    db.close()

    if not appointment:
        return jsonify({"error": "Appointment not found"}), 404

    return jsonify({
        "message": "Appointment marked as completed",
        "appointment_id": appointment.id,
        "completed_at": appointment.completed_at.isoformat()
    })
