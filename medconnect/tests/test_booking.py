def test_mobile_requires_auth_for_appointment(app_client):
    client, _ = app_client
    resp = client.post("/api/mobile/appointments", json={"doctor_id": 1, "hospital_id": 1})
    assert resp.status_code == 401
