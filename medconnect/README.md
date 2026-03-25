# MedConnect

MedConnect is a complete IVR + Web + Mobile-ready OPD booking platform.

## What is included

- **IVR APIs**: call entry, OTP, registration, hospital/doctor discovery, booking.
- **Mobile APIs**: OTP auth, bearer token sessions, patient profile onboarding, booking flow.
- **Admin APIs**: doctor availability and queue management with optional API key protection.
- **Web views**: login, admin dashboard, doctor dashboard.
- **Database models**: patient, hospital, doctor, appointment, OTP.

---

## 1) Local setup (quick start)

```bash
cd medconnect
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp config/secrets.example.env config/secrets.env
python seed.py
python app.py
```

App will run at `http://localhost:5000`.

Health check:

```bash
curl http://localhost:5000/health
```

---

## 2) Environment configuration

Use `config/secrets.env`:

- `FLASK_ENV=development|production`
- `DATABASE_URL` (SQLite/MySQL)
- `SECRET_KEY`
- `OTP_EXPIRY_SECONDS`
- `OTP_MAX_RETRIES`
- `ADMIN_API_KEY`
- `PORT`

For production, start from `config/secrets.example.env` and set strong secrets.

---

## 3) Mobile API (JSON)

Base path: `/api/mobile`

### Request OTP
`POST /api/mobile/auth/request-otp`
```json
{"phone_number": "+919999999999"}
```

### Verify OTP (get access token)
`POST /api/mobile/auth/verify-otp`
```json
{"phone_number": "+919999999999", "otp": "123456"}
```

### Register patient (Bearer token required)
`POST /api/mobile/patients/register`
```json
{"name": "Asha", "age": 28, "gender": "female"}
```

### Hospitals by pincode
`GET /api/mobile/hospitals?pincode=600001`

### Doctors by hospital
`GET /api/mobile/hospitals/<hospital_id>/doctors`

### Book appointment (Bearer token required)
`POST /api/mobile/appointments`
```json
{"doctor_id": 1, "hospital_id": 1}
```

---

## 4) Deploy with Docker

From repository root:

```bash
docker compose up --build -d
```

This launches Gunicorn on port `5000` and auto-initializes DB tables at startup.

### Production compose profile (app + MySQL)

```bash
docker compose -f docker-compose.prod.yml up --build -d
```

This profile provisions MySQL, waits for DB readiness, and starts Gunicorn only after DB is reachable.

---

## 5) Production run (without Docker)

```bash
cd medconnect
pip install -r requirements.txt
gunicorn --bind 0.0.0.0:5000 --workers 2 --threads 4 wsgi:app
```

---

## 6) Testing

```bash
pytest -q
```

Included tests cover:
- mobile OTP/register/book flow
- IVR validation failure path
- auth protection for appointment booking
- rate limiting behavior

---

## 7) Notes

- In `DEBUG` mode, OTP endpoints include `otp_debug` for testing.
- In production, integrate real SMS/WhatsApp provider and disable debug output.
- For multi-instance production, replace in-memory rate limit with Redis-backed limiter.


## 8) Useful Make targets

From repository root:

```bash
make install
make run
make seed
make test
make docker-up
make docker-prod-up
```
