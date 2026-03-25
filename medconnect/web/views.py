from flask import Blueprint, render_template, request, redirect, url_for, flash
from database.database import SessionLocal
from database.repository import (
    get_hospital_by_id,
    get_appointments_for_doctor,
    complete_appointment,
    set_doctor_availability
)

web_bp = Blueprint("web", __name__)


# -----------------------------
# Helper: DB Session
# -----------------------------
def get_db():
    return SessionLocal()


# -----------------------------
# Login Page (Mock)
# -----------------------------
@web_bp.route("/login", methods=["GET", "POST"])
def login():
    """
    Simple mock login.
    Later this can be replaced with proper auth.
    """
    if request.method == "POST":
        user_role = request.form.get("role")
        user_id = request.form.get("user_id")

        if user_role == "doctor":
            return redirect(url_for("web.doctor_dashboard", doctor_id=user_id))
        elif user_role == "admin":
            return redirect(url_for("web.admin_dashboard", hospital_id=user_id))

        flash("Invalid login details", "error")

    return render_template("login.html")


# -----------------------------
# Admin Dashboard
# -----------------------------
@web_bp.route("/admin/<int:hospital_id>")
def admin_dashboard(hospital_id):
    db = get_db()
    hospital = get_hospital_by_id(db, hospital_id)

    if not hospital:
        db.close()
        return "Hospital not found", 404

    doctors = hospital.doctors
    db.close()

    return render_template(
        "admin/hospitals.html",
        hospital=hospital,
        doctors=doctors
    )


# -----------------------------
# Update Doctor Availability
# -----------------------------
@web_bp.route("/admin/doctor/<int:doctor_id>/availability", methods=["POST"])
def update_availability(doctor_id):
    is_available = request.form.get("is_available") == "true"

    db = get_db()
    set_doctor_availability(db, doctor_id, is_available)
    db.close()

    flash("Doctor availability updated")
    return redirect(request.referrer)


# -----------------------------
# Doctor Dashboard
# -----------------------------
@web_bp.route("/doctor/<int:doctor_id>")
def doctor_dashboard(doctor_id):
    db = get_db()
    appointments = get_appointments_for_doctor(db, doctor_id)
    db.close()

    return render_template(
        "doctor/home.html",
        doctor_id=doctor_id,
        appointments=appointments
    )


# -----------------------------
# Mark Appointment Finished
# -----------------------------
@web_bp.route("/doctor/appointment/<int:appointment_id>/finish", methods=["POST"])
def finish_appointment_view(appointment_id):
    db = get_db()
    complete_appointment(db, appointment_id)
    db.close()

    flash("Appointment marked as completed")
    return redirect(request.referrer)
