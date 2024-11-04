import os
import uuid
from io import BytesIO
from typing import Dict
import base64
import jwt
from dotenv import dotenv_values
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from PIL import Image

from API.Authentication.jwt_handler import get_user_by_id, JWT_SECRET, JWT_ALGORITHM
from API.Schemas.profileModels import GetProfilesInfo, NewDescription
from API.security import manager
from storage.database import Session, User, Profile, UserStatistic
from storage.db_utils import get_db
profile_router = APIRouter(prefix="/profile", tags=["Profile Picture"])

#IMAGEDIR = "D:/Florea/Proiecte/Backend-Chess-ia-cod/Poze/"  pt cel de pe PC
env_vars = dotenv_values(".env")

IMAGEDIR = env_vars.get("IMAGEDIR")

# TODO de modificat ca la get profile(get_profile_pictures) sa imi returneze profilul + statisticile precum won,lost,draw, total moves, ultimele 10 meciuri
# TODO update and delete, get error if it is not created, get all basic images and set for each user the default photo
# TODO set a basic picture for every user, when uploading for the 2-nd time i should delete


# pentru a lua toate detaliile pentru profil
@profile_router.get("/get")
def get_profile(
        db: Session = Depends(get_db),
        user_id: str = Depends(manager)):
    user = get_user_by_id(user_id, db)
    userStatistics = db.query(UserStatistic).filter(UserStatistic.userEmail == user.email).first()
    profile = db.query(Profile).filter(user.email == Profile.userEmail).first()
    path = f"{IMAGEDIR}{profile.photoData}"
    with open(path, "rb") as f:
        path64 = base64.b64encode(f.read()).decode("utf-8")
    return {"Base64":path64,
            "Username":user.username,
            "Description":profile.description,
            "Total matches played:":userStatistics.games_played,
            "wins":userStatistics.wins,
            "Losses":userStatistics.losses,
            "Draw":userStatistics.draws,
            "Winrate":userStatistics.winrate}


# pt a incarca poza pentru profil
@profile_router.post("/upload/")
async def create_upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user_id: str = Depends(manager)
):
    try:
        user = get_user_by_id(user_id, db)
        profile = db.query(Profile).filter(Profile.userEmail == user.email).first()

        if profile and profile.photoData:
            file_path = os.path.join(IMAGEDIR, profile.photoData)
            if os.path.exists(file_path) and profile.photoData != "basic.jpg":
                os.remove(file_path)

        photo_id = str(uuid.uuid4())
        file.filename = f"{photo_id}.jpg"
        allowed_formats = ["image/png", "image/jpeg", "image/jpg"]

        if file.content_type not in allowed_formats:
            profile.photoData = "basic.jpg"
            db.commit()
            db.refresh(profile)
            raise HTTPException(status_code=415, detail="Invalid photo format. Allowed formats: PNG, JPEG, JPG")

        contents = await file.read()
        image = Image.open(BytesIO(contents))
        # pentru a evita pozele care nu sunt de tipul RGB de exemplu, spiderman.png
        if image.mode != "RGB":
            image = image.convert("RGB")

        target_width, target_height = 128, 128
        image = image.resize((target_width, target_height))

        file_path = os.path.join(IMAGEDIR, file.filename)
        with open(file_path, "wb") as f:
            image.save(f, format='JPEG')

        if profile:
            profile.photoData = file.filename
            db.commit()
            db.refresh(profile)
        else:
            new_profiledata = Profile(
                profile_id=photo_id,
                photoData=file.filename,
                userEmail=user.email,
                description=profile.description
            )
            db.add(new_profiledata)
            db.commit()
            db.refresh(new_profiledata)

        return {"filename": file.filename}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# pentru a lua detaliile unui meci( poza white, poza black, nume white, nume black)
@profile_router.post("/get_both_pictures", response_model=Dict[str, str])
def get_profile_pictures(
        data: GetProfilesInfo,
        db: Session = Depends(get_db)):

    myPayload = jwt.decode(data.myJWT, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    myEmail = myPayload["email"]
    myUser = db.query(User).filter(User.email == myEmail).first()
    caller_photo = db.query(Profile).filter(Profile.userEmail == myEmail).first()
    myStatistic = db.query(UserStatistic).filter(UserStatistic.userEmail == myEmail).first()

    otherPayload = jwt.decode(data.otherJWT, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    otherEmail = otherPayload["email"]
    otherUser = db.query(User).filter(User.email == otherEmail).first()
    requested_user = db.query(Profile).filter(Profile.userEmail == otherEmail).first()
    otherStatistic = db.query(UserStatistic).filter(UserStatistic.userEmail == otherEmail).first()

    if requested_user:
        requested_user_path = f"{IMAGEDIR}{requested_user.photoData}"
        caller_path = f"{IMAGEDIR}{caller_photo.photoData}"

        with open(requested_user_path, "rb") as f:
            requested_user_base64 = base64.b64encode(f.read()).decode("utf-8")
        with open(caller_path, "rb") as f:
            caller_base64 = base64.b64encode(f.read()).decode("utf-8")

        my_wins = str(myStatistic.wins)
        other_wins = str(otherStatistic.wins)
        my_losses = str(myStatistic.losses)
        other_losses = str(otherStatistic.losses)

        return {"caller_profile_picture": caller_base64, "requested_profile_picture": requested_user_base64,
                "myName": myUser.username, "otherName": otherUser.username,
                "myWins": my_wins, "otherWins": other_wins,
                "myLosses": my_losses, "otherLosses": other_losses}
    else:
        raise HTTPException(status_code=404, detail="ERROR: Requested user or profile pictures not found")


@profile_router.put("/update_description")
def update_description(
        data: NewDescription,
        user_id: str = Depends(manager),
        db: Session = Depends(get_db)):

    user = get_user_by_id(user_id,db)
    user_profile = db.query(Profile).filter(Profile.userEmail == user.email).first()
    user_profile.description = data.newDescription
    db.commit()
    db.refresh(user_profile)
    return {"message":"Succesful!"}
