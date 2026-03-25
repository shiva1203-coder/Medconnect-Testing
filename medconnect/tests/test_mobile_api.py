from database.database import SessionLocal
from database.models import Hospital, Doctor


def test_mobile_register_and_book_flow(app_client):
    client, _ = app_client

    resp = client.post("/api/mobile/auth/request-otp", json={"phone_number": "+919999999999"})
    assert resp.status_code == 200
    otp = resp.get_json()["otp_debug"]

    verify = client.post(
        "/api/mobile/auth/verify-otp",
        json={"phone_number": "+919999999999", "otp": otp},
    )
    assert verify.status_code == 200
    token = verify.get_json()["access_token"]

    reg = client.post(
        "/api/mobile/patients/register",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "Asha", "age": 27, "gender": "female"},
    )
    assert reg.status_code == 201

    db = SessionLocal()
    try:
        hospital = Hospital(name="City Care", pincode="600001", address="Central")
        db.add(hospital)
        db.commit()
        doctor = Doctor(name="Dr Ravi", department="General", hospital_id=hospital.id, is_available=True)
        db.add(doctor)
        db.commit()

        hospitals = client.get("/api/mobile/hospitals?pincode=600001")
        assert hospitals.status_code == 200
        assert len(hospitals.get_json()["hospitals"]) == 1

        doctors = client.get(f"/api/mobile/hospitals/{hospital.id}/doctors")
        assert doctors.status_code == 200
        assert len(doctors.get_json()["doctors"]) == 1

        booking = client.post(
            "/api/mobile/appointments",
            headers={"Authorization": f"Bearer {token}"},
            json={"doctor_id": doctor.id, "hospital_id": hospital.id},
        )
        assert booking.status_code == 201
        assert booking.get_json()["status"] == "BOOKED"
    finally:
        db.close()
