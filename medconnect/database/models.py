from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime,
    ForeignKey, UniqueConstraint
)
from sqlalchemy.orm import relationship
from datetime import datetime

from database.database import Base


# -----------------------------
# Patient Table
# -----------------------------
class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String(15), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(String(10), nullable=False)

    # Aadhaar (encrypted, optional)
    aadhaar_hash = Column(String(256), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    appointments = relationship("Appointment", back_populates="patient")


# -----------------------------
# Hospital Table
# -----------------------------
class Hospital(Base):
    __tablename__ = "hospitals"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    pincode = Column(String(10), nullable=False)
    address = Column(String(255), nullable=False)

    doctors = relationship("Doctor", back_populates="hospital")


# -----------------------------
# Doctor Table
# -----------------------------
class Doctor(Base):
    __tablename__ = "doctors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    department = Column(String(100), nullable=False)
    is_available = Column(Boolean, default=True)

    hospital_id = Column(Integer, ForeignKey("hospitals.id"))
    hospital = relationship("Hospital", back_populates="doctors")

    appointments = relationship("Appointment", back_populates="doctor")


# -----------------------------
# Appointment / OPD Token Table
# -----------------------------
class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    token_number = Column(String(20), nullable=False)
    appointment_time = Column(DateTime, nullable=False)

    status = Column(String(20), default="BOOKED")
    # BOOKED → COMPLETED → CANCELLED

    patient_id = Column(Integer, ForeignKey("patients.id"))
    doctor_id = Column(Integer, ForeignKey("doctors.id"))
    hospital_id = Column(Integer, ForeignKey("hospitals.id"))

    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    patient = relationship("Patient", back_populates="appointments")
    doctor = relationship("Doctor", back_populates="appointments")
    hospital = relationship("Hospital")

    __table_args__ = (
        UniqueConstraint("token_number", "hospital_id", name="uq_token_hospital"),
    )


# -----------------------------
# OTP Table (Temporary)
# -----------------------------
class OTP(Base):
    __tablename__ = "otps"

    id = Column(Integer, primary_key=True)
    phone_number = Column(String(15), nullable=False)
    otp_code = Column(String(10), nullable=False)
    attempts = Column(Integer, default=0)
    expires_at = Column(DateTime, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)
