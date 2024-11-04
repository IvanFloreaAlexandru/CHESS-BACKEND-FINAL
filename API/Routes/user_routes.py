import datetime
import re
import uuid
from urllib.parse import quote

import bcrypt
import jwt
from fastapi import APIRouter, Depends, HTTPException, Form
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import and_
from sqlalchemy.orm import Session
from fastapi import BackgroundTasks
from starlette.requests import Request
from starlette.responses import HTMLResponse, RedirectResponse
from starlette.templating import Jinja2Templates

from API.Emailing.emailing2 import send_email, HOST, PORT, FROM_EMAIL, GOOGLE_APP_PASSWORD
from API.Forgot_password.passwordreset import generate_password_reset_token, SECRET_KEY, ALGORITHM
from API.TwoFactor.TwoFactor import verify_totp_code_endpoint, TOTPVerificationRequest
from API.Authentication.jwt_handler import sign_jwt, get_user_by_id
from API.Schemas.userModel import UserCreate, UserModify, UserGet, UserRecovery
from API.Schemas.userModel import UserResponse
from API.Websockets.Rooms import room_manager
from API.security import manager
from storage.db_utils import get_db
from storage.database import User, UserSetting, UserStatistic, Profile, Achievements
from better_profanity import profanity

user_router = APIRouter(tags=["Users"])

global_salt = "$2b$12$nrBd3QtspO23j7x.8.8Cuu"


# TODO sa fac profanity pentru toate limbile posibile si pentru imagini la fel

# TODO sugestie pentru verificarea daca un email este valid ( folosirea librariei verify-email )

@user_router.post("/create_user", response_model=UserResponse)
def create_user(user_data: UserCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    if not re.match(r"[^@]+@[^@]+\.[^@]+", user_data.email):
        raise HTTPException(status_code=400, detail="Invalid email format")
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(status_code=400, detail="Email already exists")

    if profanity.contains_profanity(user_data.username):
        raise HTTPException(status_code=400, detail="Username contains profanity")
    user_id = str(uuid.uuid4())
    hashed_password = bcrypt.hashpw(user_data.password.encode('utf-8'), global_salt.encode('utf-8'))
    timenow = datetime.datetime.now()
    timeGoodFormat = timenow.strftime("%Y-%m-%d")
    # TODO de refacut mesajul asta cu email template
    message = (f"Hello {user_data.email},\n\nWelcome to CHESS.RO!\n\nYour account has been successfully created. To "
               f"verify your account, please click the link below:\n\n\n\nThis link will expire after a certain "
               f"period for security reasons, so please make sure to use it promptly.\n\nIf you did not request this "
               f"verification, you can safely ignore this email. Your account remains secure.\n\nThank you,\nCHESS.RO")

    background_tasks.add_task(
        send_email,
        HOST, PORT, FROM_EMAIL, GOOGLE_APP_PASSWORD,
        user_data.email,
        "Account Verification Link",
        message
    )

    db_user = User(
        user_id=user_id,
        username=user_data.username,
        password=hashed_password.decode('utf-8'),
        email=user_data.email,
        registration_date=timeGoodFormat,
        is_verified=False,
        warningsNumber=0,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    db_statistic = UserStatistic(
        user_statistics_id=str(uuid.uuid4()),
        userEmail=user_data.email,
        games_played=0,
        draws=0,
        losses=0,
        points=0
    )
    db.add(db_statistic)
    db.commit()
    db.refresh(db_statistic)
    db_user_setting = UserSetting(
        user_setting_id=str(uuid.uuid4()),
        userEmail=user_data.email,
        itemsPurchased="",
        settings=""
    )
    db.add(db_user_setting)
    db.commit()
    db.refresh(db_user_setting)

    profile = Profile(
        profile_id=str(uuid.uuid4()),
        photoData="/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgNDRgyIRwhMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjL/wAARCACAAIADASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL/8QAtREAAgECBAQDBAcFBAQAAQJ3AAECAxEEBSExBhJBUQdhcRMiMoEIFEKRobHBCSMzUvAVYnLRChYkNOEl8RcYGRomJygpKjU2Nzg5OkNERUZHSElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6goOEhYaHiImKkpOUlZaXmJmaoqOkpaanqKmqsrO0tba3uLm6wsPExcbHyMnK0tPU1dbX2Nna4uPk5ebn6Onq8vP09fb3+Pn6/9oADAMBAAIRAxEAPwD5/ooooAKKKKACuj8PeEL3XMTufs9n/wA9WGS3+6O/16UnhDw9/bmpb51b7HBhpCP4j2X8f5V66iLGioihUUYCqMACgDE07wjo2mou20WeQdZJxvJ/DoPyraVFRdqKqj0UYp1FADWRXXa6qw9GGaxdS8I6NqSNutFgkPSSAbCPw6H8q3KKAPIfEPhG90PMyn7RZ/8APVRgr7MO316Vzte/OiyIyOoZGGGVhkEV5F4u8P8A9hamDCGNpPloif4T3X8P5UAc9RRRQAUUUUAFFFFABRRTkXfIq+pAoA9i8I6b/Znhy2RlxLKPOk+rdP0xW5TUQRxqg6KAB+FOoAKKKKACiiigArD8Xab/AGl4cuUVcyRDzo/qvX9M1uU10EkbIejAg/jQB4DRTpF2SMvoSKbQAUUUUAFFFFABTo22SK3oQabRQB7+jB0Vx0YAilrF8J6iNT8OWshOZI18qT6rx/LBraoAKKKKACiiigApsjiOJ3JwFUkn6CnVheL9RGm+G7lwwEkw8lPq3X9M0AeOsxZix6k5pKKKACiiigAooooAKKKKAOk8H+If7E1Ex3DH7FPw/wDsN2b/AB9q9bVgyhlIKkZBB4IrwCum8O+MrvRVW3mU3NmOkZOGT/dP9KAPWqKyNO8T6PqaKYb2NHP/ACzlOxh+fX8K1x8wBXkHoRQAUUMQilmO0DueKx9Q8UaPpqMZb2N3HSOE72P5dPxoA13dY0Z3YKijJZjgAV5F4u8QnXNRCwlhZwZWMH+I92/H+VO8ReMLvXAbeMG3sv8AnkDkv7sf6VzdABRRRQAUUUUAFFFFABRRRQAUUUUAFTJd3MS7Y7iVF9FcgVDRQBLJdXEq7ZJ5XX0ZyaioooAKKKKACiiigAooooAKKK09G0G+1y4MdpGNq/flc4Vfqf6UAZlSwW090+y3hklb0RSx/SvUtL8B6TYBXuVN5MOSZOEz7L/jmumiijgQJDGkaDoqKAP0oA8fh8Ha/PgjTpFB7yMq/wAzVyP4fa64+ZbdP96X/DNer0UAeXL8OdYIyZ7MH03t/wDE09fhvqpPzXVmo9dzH+lenUUAeYv8N9UGNl3Zt9WYf0pp+HGrgEiezJ9N7f8AxNeoUUAeUv8AD7XUHyrbP/uy/wCOKpTeDdfhznTncDvGyt/I17HRQB4JPa3Fq+y4gkib0dCv86ir36SOOZCkqLIp/hdQR+tczqvgTSr8M9sps5j0MfKZ91/wxQB5PRWnrOg32h3Aju4xtb7kqHKt9D/SsygDT0DRpdc1WO0jO1PvSv8A3UHU/WvZbKyt9Os47S1jEcMYwB/U+prm/AGmLaaD9sK/vrtiSf8AZBwB/M/jXWUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAV72yt9Rs5LW6jEkMgwVP8x6GvG9f0WXQtUe1kO5D80T/AN5e3417ZXKeP9MW70H7WF/e2jbgf9kkA/0P4UAdFp1r9i0y1tf+eMSoceoHNWaKKACiiigAooooAKKKKACiiigAooooAKKKKACq2oWovdNubU4/fRMgz6kcVZooA//Z",
        userEmail=db_user.email,
        description="Hi! This is the basic description!"
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)

    achievements = Achievements(user_id=user_id,
                                achievement_id=str(uuid.uuid4()))
    db.add(achievements)
    db.commit()
    db.refresh(achievements)

    return UserResponse(
        user_id=db_user.user_id,
        username=db_user.username,
        email=db_user.email,
        password=db_user.password,
        registration_date=db_user.registration_date,
    )


@user_router.get("/verify/{token}")
def verify_account(token: str, db: Session = Depends(get_db)):
    try:
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_email = decoded_token["email"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=400, detail="Invalid token")

    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.is_verified:
        return {"message": "Account is already verified"}

    user.is_verified = True
    db.commit()

    return {"message": "Account verified successfully"}


@user_router.get("/send_verification_email/{client_jwt}")
def send_verification_email(client_jwt: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    try:
        decoded_token = jwt.decode(client_jwt, SECRET_KEY, algorithms=[ALGORITHM])
        email = decoded_token["email"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=400, detail="Invalid token")

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    verification_token = jwt.encode({"email": email}, SECRET_KEY, algorithm=ALGORITHM)
    verification_link = f"http://localhost:8000/verify/{quote(verification_token)}"

    message = templates.TemplateResponse("verify_account.html", {
        "request": None,
        "user_email": user.email,
        "verification_link": verification_link
    }).body.decode('utf-8')

    background_tasks.add_task(
        send_email,
        HOST, PORT, FROM_EMAIL, GOOGLE_APP_PASSWORD,
        user.email,
        "Verify your account",
        message
    )

    return {"message": "Verification email sent"}


# Asta e cea mai importanta la data : OAuth2PasswordRequestForm = Depends() pentru logarea
# din swagger ui


'''@user_router.post("/login")
async def login(data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.username).first()
    if user:
        stored_hashed_password = user.password.encode('utf-8')
        if bcrypt.checkpw(data.password.encode('utf-8'), stored_hashed_password):
            if data.totp_code and user.twoFactor:
                response_totp = await verify_totp_code_endpoint(
                    request=TOTPVerificationRequest(totp_code=data.totp_code),
                    db=db, user_id=user.user_id)
                if response_totp.get("message") == "Authentication successful!":
                    jwt_token = sign_jwt(data.username, user.user_id)
                    response = JSONResponse(content={"message": "Login successful"})
                    response.set_cookie(key="access_token", value=jwt_token, httponly=True, secure=True,
                                        samesite="lax", path="/", expires=1)
                    print(f"Set cookie: {response.headers.get('Set-Cookie')}")
                    return response
                else:
                    raise HTTPException(status_code=401, detail="Authentication failed")
            else:
                if not user.twoFactor:
                    jwt_token = sign_jwt(data.username, user.user_id)
                    response = JSONResponse(content={"message": "Login successful"})
                    response.set_cookie(key="access_token", value=jwt_token, httponly=True, secure=True,
                                        samesite="lax", path="/", expires=1)
                    print(f"Set cookie: {response.headers.get('Set-Cookie')}")
                    return response
                else:
                    raise HTTPException(status_code=400, detail="Authentication failed, you haven't put the totp code "
                                                                "and you have the twoFactor activated")
        else:
            raise HTTPException(status_code=401, detail="Invalid email or password")
    else:
        raise HTTPException(status_code=401, detail="Invalid email or password")'''

'''@user_router.post("/login")
async def login(data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.username).first()
    if user:
        stored_hashed_password = user.password.encode('utf-8')
        if bcrypt.checkpw(data.password.encode('utf-8'), stored_hashed_password):
            if not user.twoFactor:
                jwt_token = sign_jwt(data.username, user.user_id)
                response = JSONResponse(content={"message": "Login successful"})
                response.set_cookie(key="access_token", value=jwt_token,httponly=True,samesite="lax")
                print(f"Set cookie: {response.headers.get('Set-Cookie')}")
                return response
            else:
                raise HTTPException(status_code=400,
                                    detail="Two-factor authentication is enabled, but no TOTP code provided")
        else:
            raise HTTPException(status_code=401, detail="Invalid email or password")
    else:
        raise HTTPException(status_code=401, detail="Invalid email or password")



@user_router.get("/status")
async def status():
    URL = "http://http://25.49.228.147:5173/login"
    cookie_jar = http.cookiejar.CookieJar()
    url_opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar))
    url_opener.open(URL)
    for cookie in cookie_jar:
        print("[ Cookie Name = %s] -- [Cookie Value = %s" % (cookie.name, cookie.value))'''


@user_router.post("/login")
async def login(data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.username).first()
    if user:
        stored_hashed_password = user.password.encode('utf-8')
        if bcrypt.checkpw(data.password.encode('utf-8'), stored_hashed_password):
            if user.twoFactor:
                raise HTTPException(status_code=400, detail="2FA required. Please verify with TOTP.")
            return sign_jwt(data.username, user.user_id)
        else:
            raise HTTPException(status_code=401, detail="Invalid email or password")
    else:
        raise HTTPException(status_code=401, detail="Invalid email or password")

# TODO de integrat si cu frontend-ul, de vazut logica apelarii endpoint-urilor
@user_router.post("/verify-totp")
async def verify_totp(data: TOTPVerificationRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.user_id == data.user_id).first()
    if not user or not user.twoFactor:
        raise HTTPException(status_code=400, detail="TOTP not enabled for this user")

    response = await verify_totp_code_endpoint(request=data, db=db, user_id=user.user_id)
    if response.get("message") == "Authentication successful!":
        return sign_jwt(user.email, user.user_id)
    else:
        raise HTTPException(status_code=401, detail="TOTP verification failed")


@user_router.get("/get_user_info/", response_model=UserGet)
def get_user_info(
        db: Session = Depends(get_db),
        user_id: str = Depends(manager)
) -> UserGet:
    print(user_id)
    user = get_user_by_id(user_id, db)
    return UserGet(
        username=user.username,
        email=user.email,
        registration_date=user.registration_date,
    )


@user_router.put("/update_user_info", response_model=UserModify)
def update_user_info(
        data: UserModify,
        db: Session = Depends(get_db),
        user_id: str = Depends(manager)
) -> UserModify:
    user = get_user_by_id(user_id, db)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    hashed_password = bcrypt.hashpw(data.password.encode('utf-8'), global_salt.encode('utf-8'))

    user.password = hashed_password.decode('utf-8')
    db.commit()
    db.refresh(user)

    return UserModify(
        password=user.password
    )


# TODO de verificat user = get_user_by_id(user_id, db) deoarece cred ca nu mai are rost din cauza la jwt-uri / manager
@user_router.delete("/delete_user/")
def delete_user(
        db: Session = Depends(get_db),
        user_id: str = Depends(manager)
):
    user = get_user_by_id(user_id, db)
    if not user:
        raise HTTPException(status_code=404, detail="D1")

    user_setting = db.query(UserSetting).filter(and_(UserSetting.userEmail == user.email)).first()

    if user_setting:
        db.delete(user_setting)
        db.commit()
    statistic = db.query(UserStatistic).filter(and_(UserStatistic.userEmail == user.email)).first()

    if statistic:
        db.delete(statistic)
        db.commit()

    profile = db.query(Profile).filter(and_(Profile.userEmail == user.email)).first()
    if profile:
        db.delete(profile)
        db.commit()
    achievements = db.query(Achievements).filter(and_(Achievements.user_id == user_id)).first()
    if achievements:
        db.delete(achievements)
        db.commit()
    db.delete(user)
    db.commit()
    return {"message": "User and associated settings deleted successfully"}


templates = Jinja2Templates(directory="templates")


@user_router.get("/forgot_password")
def forgot_password(
        data: UserRecovery,
        background_tasks: BackgroundTasks,
        db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == data.email).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    '''if not user.is_verified:
        raise HTTPException(status_code=403, detail="User not verified")'''

    token = generate_password_reset_token(data.email)
    reset_link = f"http://172.16.1.40:8000/reset_password?token={token}"

    message = templates.TemplateResponse("password_reset_email.html", {
        "request": None,
        "user_email": user.email,
        "reset_link": reset_link
    }).body.decode('utf-8')

    background_tasks.add_task(
        send_email,
        HOST, PORT, FROM_EMAIL, GOOGLE_APP_PASSWORD,
        user.email,
        "Password Reset Link",
        message
    )
    return {"message": f"Password reset link sent to your email {user.email}"}


# TODO sa ma uit la ce facea asta de mai jos

# TODO de modificat ca sa se ceara userul logat nu token : str,  si pe postman la fel la categoria Users - reset_passwoord
@user_router.get("/reset_password", response_class=HTMLResponse)
async def reset_password_form(request: Request, token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload["email"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=400, detail="Invalid token")

    return RedirectResponse(url=f"http://your-frontend-domain.com/reset-password?token={token}")


@user_router.post("/update_password")
async def update_password(
        token: str = Form(...),
        new_password: str = Form(...),
        confirm_password: str = Form(...),
        db: Session = Depends(get_db)
):
    if new_password != confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload["email"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=400, detail="Invalid token")

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
    user.password = hashed_password.decode('utf-8')
    db.commit()

    return {"message": "Password updated successfully"}


'''@user_router.post("/disconnect_ws/")
async def disconnect_ws(
        token
):
    await room_manager.disconnect(token)'''
