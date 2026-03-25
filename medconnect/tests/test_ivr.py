def test_ivr_rejects_invalid_phone(app_client):
    client, _ = app_client
    resp = client.post("/ivr/call", json={"from": "invalid"})
    assert resp.status_code == 400
    assert "error" in resp.get_json()
