from dotenv import load_dotenv
load_dotenv("config/secrets.env")

from datetime import datetime, timedelta
from database.database import init_db, SessionLocal, create_all

import database.database as db_core
from database.models import Hospital, Doctor, Patient, Appointment

from dotenv import load_dotenv
load_dotenv("config/secrets.env")

from datetime import datetime, timedelta
import database.database as db_core
from database.models import Hospital, Doctor, Patient, Appointment


def seed():
    print("\n🚀 Starting MedConnect Seeder...\n")

    # Initialize Database
    db_core.init_db()
    db_core.create_all()

    db = db_core.SessionLocal()

    try:
        print("Seeding demo data...\n")

        existing_hospital = db.query(Hospital).first()
        if existing_hospital:
            print("✅ Demo data already exists. Skipping seeding.")
            return

        hospital1 = Hospital(
            name="City Care Hospital",
            pincode="600001",
            address="Chennai Central"
        )

        hospital2 = Hospital(
            name="MedLife Clinic",
            pincode="600001",
            address="Chennai Egmore"
        )

        db.add_all([hospital1, hospital2])
        db.commit()

        doctor1 = Doctor(
            name="Dr. Ravi Kumar",
            department="General Medicine",
            is_available=True,
            hospital_id=hospital1.id
        )

        doctor2 = Doctor(
            name="Dr. Meena",
            department="Pediatrics",
            is_available=True,
            hospital_id=hospital1.id
        )

        doctor3 = Doctor(
            name="Dr. Arun",
            department="Orthopedics",
            is_available=True,
            hospital_id=hospital2.id
        )

        db.add_all([doctor1, doctor2, doctor3])
        db.commit()

        patient = Patient(
            phone_number="+919999999999",
            name="Demo Patient",
            age=35,
            gender="Male"
        )

        db.add(patient)
        db.commit()

        appointment = Appointment(
            token_number="TOKEN-001",
            appointment_time=datetime.utcnow() + timedelta(minutes=10),
            status="BOOKED",
            patient_id=patient.id,
            doctor_id=doctor1.id,
            hospital_id=hospital1.id
        )

        db.add(appointment)
        db.commit()

        print("✅ Demo data seeded successfully!\n")

        print("Doctor IDs:")
        print(f"Dr Ravi → {doctor1.id}")
        print(f"Dr Meena → {doctor2.id}")
        print(f"Dr Arun → {doctor3.id}")

    finally:
        db.close()
        print("\n✅ Seeder finished safely.\n")


if __name__ == "__main__":
    seed()
