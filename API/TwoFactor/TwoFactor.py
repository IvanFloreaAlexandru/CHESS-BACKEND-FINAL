from fastapi import HTTPException, APIRouter, Depends
from pydantic import BaseModel
import pyotp
import qrcode
import io

from starlette.responses import StreamingResponse

from API.Authentication.jwt_handler import get_user_by_id
from API.Emailing.emailing import send_email_with_attachment, HOST, FROM_EMAIL, GOOGLE_APP_PASSWORD
from API.security import manager
from storage.database import Session
from storage.db_utils import get_db

two_factor = APIRouter(tags=["2Factor"])


class TOTPVerificationRequest(BaseModel):
    totp_code: str


def generate_secret_key():
    return pyotp.random_base32()


def generate_qr_code_url(user_email, secret_key):
    return pyotp.totp.TOTP(secret_key).provisioning_uri(user_email, issuer_name="Chess.ro")


def verify_totp_code(user_secret_key, totp_code):
    totp = pyotp.TOTP(user_secret_key)
    return totp.verify(totp_code)


def generate_qr_code(uri):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(uri)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    return buffer


@two_factor.post("/generate-qr-code")
async def generate_qr_code_endpoint(
        db: Session = Depends(get_db),
        user_id: str = Depends(manager)):
    user = get_user_by_id(user_id, db)
    if not user.twoFactor:
        if not user.twoFactorCode:
            user_secret_key = generate_secret_key()
            qr_code_url = generate_qr_code_url(user.email, user_secret_key)
            qr_code_image_buffer = generate_qr_code(qr_code_url)
            await send_email_with_attachment(HOST, 587, FROM_EMAIL,
                                             GOOGLE_APP_PASSWORD, user.email,
                                             '2 Factor', 'Here is your QrCode', qr_code_image_buffer)

            user.twoFactorCode = user_secret_key
            db.commit()
            db.refresh(user)
            print(user_secret_key)
            return StreamingResponse(io.BytesIO(qr_code_image_buffer.getvalue()), media_type="image/png")
        else:
            raise HTTPException(status_code=400, detail="User has already tried to receive the QR CODE")
    else:
        raise HTTPException(status_code=400, detail="User has already activated 2FACTOR")


@two_factor.post("/verify-totp-code")
async def verify_totp_code_endpoint(
        request: TOTPVerificationRequest,
        db: Session = Depends(get_db),
        user_id: str = Depends(manager)):

    user = get_user_by_id(user_id, db)
    if not user:
        raise HTTPException(status_code=400, detail="User not found")
    if verify_totp_code(user.twoFactorCode, request.totp_code):
        user.twoFactor = True
        db.commit()
        db.refresh(user)
        return {"message": "Authentication successful!"}
    else:
        raise HTTPException(status_code=401, detail="Authentication failed")
