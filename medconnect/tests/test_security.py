def test_rate_limit_blocks_after_threshold(app_client):
    client, _ = app_client
    payload = {"phone_number": "+919999999999"}
    last_status = None
    for _ in range(6):
        response = client.post("/api/mobile/auth/request-otp", json=payload)
        last_status = response.status_code

    assert last_status == 429
