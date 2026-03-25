from sqlalchemy.orm import Session
from datetime import datetime

from database.models import (
    Patient,
    Hospital,
    Doctor,
    Appointment,
    OTP
)

# -----------------------------
# Patient Operations
# -----------------------------

def get_patient_by_phone(db: Session, phone_number: str):
    return db.query(Patient).filter(Patient.phone_number == phone_number).first()


def create_patient(db: Session, phone_number: str, name: str, age: int, gender: str, aadhaar_hash=None):
    patient = Patient(
        phone_number=phone_number,
        name=name,
        age=age,
        gender=gender,
        aadhaar_hash=aadhaar_hash
    )
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient


# -----------------------------
# Hospital Operations
# -----------------------------

def get_hospitals_by_pincode(db: Session, pincode: str):
    return db.query(Hospital).filter(Hospital.pincode == pincode).all()


def get_hospital_by_id(db: Session, hospital_id: int):
    return db.query(Hospital).filter(Hospital.id == hospital_id).first()


# -----------------------------
# Doctor Operations
# -----------------------------

def get_available_doctors(db: Session, hospital_id: int):
    return (
        db.query(Doctor)
        .filter(
            Doctor.hospital_id == hospital_id,
            Doctor.is_available.is_(True)
        )
        .all()
    )


def set_doctor_availability(db: Session, doctor_id: int, is_available: bool):
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if doctor:
        doctor.is_available = is_available
        db.commit()
    return doctor


# -----------------------------
# Appointment / OPD Operations
# -----------------------------

def create_appointment(
    db: Session,
    patient_id: int,
    doctor_id: int,
    hospital_id: int,
    token_number: str,
    appointment_time: datetime
):
    appointment = Appointment(
        patient_id=patient_id,
        doctor_id=doctor_id,
        hospital_id=hospital_id,
        token_number=token_number,
        appointment_time=appointment_time
    )
    db.add(appointment)
    db.commit()
    db.refresh(appointment)
    return appointment


def get_appointments_for_doctor(db: Session, doctor_id: int):
    return (
        db.query(Appointment)
        .filter(
            Appointment.doctor_id == doctor_id,
            Appointment.status == "BOOKED"
        )
        .order_by(Appointment.appointment_time)
        .all()
    )


def complete_appointment(db: Session, appointment_id: int):
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if appointment:
        appointment.status = "COMPLETED"
        appointment.completed_at = datetime.utcnow()
        db.commit()
    return appointment


# -----------------------------
# OTP Operations
# -----------------------------

def create_otp(db: Session, phone_number: str, otp_code: str, expires_at: datetime):
    otp = OTP(
        phone_number=phone_number,
        otp_code=otp_code,
        expires_at=expires_at
    )
    db.add(otp)
    db.commit()
    return otp


def get_valid_otp(db: Session, phone_number: str):
    return (
        db.query(OTP)
        .filter(
            OTP.phone_number == phone_number,
            OTP.expires_at > datetime.utcnow()
        )
        .order_by(OTP.created_at.desc())
        .first()
    )


def increment_otp_attempts(db: Session, otp: OTP):
    otp.attempts += 1
    db.commit()
    return otp


def delete_otp(db: Session, otp: OTP):
    db.delete(otp)
    db.commit()
