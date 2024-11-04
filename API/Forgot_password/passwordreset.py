import datetime
import jwt

SECRET_KEY = "cdf6d7aa26172376a082d738eb67c93b"
ALGORITHM = "HS256"
TOKEN_EXPIRATION_TIME_MINUTES = 5


def generate_password_reset_token(email: str) -> str:
    now = datetime.datetime.now(datetime.UTC)
    expires_delta = datetime.timedelta(minutes=TOKEN_EXPIRATION_TIME_MINUTES)
    expires_at = now + expires_delta
    payload = {
        "email": email,
        "exp": expires_at
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
