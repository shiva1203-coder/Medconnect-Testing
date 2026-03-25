from datetime import datetime, timedelta
from database.repository import create_appointment


def book_next_slot(db, patient_id: int, doctor_id: int, hospital_id: int):
    appointment_time = datetime.utcnow() + timedelta(minutes=30)
    token_number = f"TOKEN-{datetime.utcnow().strftime('%H%M%S')}"
    return create_appointment(
        db,
        patient_id=patient_id,
        doctor_id=doctor_id,
        hospital_id=hospital_id,
        token_number=token_number,
        appointment_time=appointment_time,
    )
