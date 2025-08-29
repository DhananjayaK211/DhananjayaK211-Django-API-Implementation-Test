# AIEngineer Django Auth API (Cookie + CSRF + OTP)

Cookie-based authentication with Django + DRF, OTP email verification, and Swagger UI that sets a CSRF cookie on load.

All endpoints were tested using **Postman**:
- Register with email/password (`POST /api/register/`), sends OTP (console email backend in dev)
- Verify OTP (`POST /api/register/verify/`)
- Login with email/password (`POST /api/login/`) → sets `auth_token` HttpOnly+Secure cookie
- Get current user (`GET /api/me/`) using cookie authentication
- Logout (`POST /api/logout/`) → clears cookie
- Swagger at `/swagger/` sets a CSRF cookie automatically (via `ensure_csrf_cookie`)

## Requirements
- Python 3.10+ (tested with 3.11)
- pip / venv

## Quickstart

```bash
# 1) Clone the repository
git clone <your-repo-url> ai_auth
cd ai_auth

# 2) Create & activate virtual environment
python -m venv .venv
# Windows:
.venv\Scripts\activate

# 3) Install dependencies
pip install -r requirements.txt

# 4) Run migrations
python manage.py migrate

# 5) (Optional) create admin user
python manage.py createsuperuser

# 6) Start server
python manage.py runserver 0.0.0.0:8000
