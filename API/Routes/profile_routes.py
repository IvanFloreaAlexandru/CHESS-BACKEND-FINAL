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

IMAGEDIR = os.path.join(os.path.dirname(__file__), 'Poze/')


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
    profile = db.query(Profile).filter(Profile.userEmail == user.email).first()

    # Verificăm dacă profilul există
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    # Verificăm dacă poza există în baza de date
    if not profile.photoData:
        raise HTTPException(status_code=404, detail="Profile picture not found in database")

    # Poza este stocată în Base64, deci o putem returna direct
    return {
        "Base64": profile.photoData,  # Direct din modelul Profile
        "Username": user.username,
        "Description": profile.description,
        "Total Matches Played": userStatistics.games_played,
        "Wins": userStatistics.wins,
        "Losses": userStatistics.losses,
        "Draws": userStatistics.draws,
        "Winrate": userStatistics.winrate
    }



# pt a incarca poza pentru profil
@profile_router.post("/upload/")
async def create_upload_file(
        file: UploadFile = File(...),
        db: Session = Depends(get_db),
        user_id: str = Depends(manager)
):
    user = get_user_by_id(user_id, db)
    profile = db.query(Profile).filter(Profile.userEmail == user.email).first()

    # Verificăm tipul fișierului
    allowed_formats = ["image/png", "image/jpeg", "image/jpg"]
    if file.content_type not in allowed_formats:
        raise HTTPException(status_code=415, detail="Invalid photo format. Allowed formats: PNG, JPEG, JPG")

    # Citim conținutul fișierului și îl convertim în Base64
    contents = await file.read()
    image = Image.open(BytesIO(contents))

    if image.mode != "RGB":
        image = image.convert("RGB")

    # Redimensionăm imaginea
    target_width, target_height = 128, 128
    image = image.resize((target_width, target_height))

    # Salvăm imaginea în format Base64
    buffered = BytesIO()
    image.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")

    # Salvăm datele în baza de date
    if profile:
        profile.photoData = img_str  # Stocăm Base64 în câmpul photoData
    else:
        new_profile = Profile(
            photoData=img_str,
            userEmail=user.email,
            description=profile.description
        )
        db.add(new_profile)

    db.commit()
    return {"message": "Photo uploaded successfully!"}


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

    if requested_user and caller_photo:
        requested_user_base64 = requested_user.photoData  # Asigură-te că acesta este un path către fișier
        caller_base64 = caller_photo.photoData  # Asigură-te că acesta este un path către fișier

        # Citim fișierul pentru imaginea utilizatorului solicitat


        return {
            "myName": myUser.username,
            "otherName": otherUser.username,
            "myWins": str(myStatistic.wins),  # Convertim în string
            "otherWins": str(otherStatistic.wins),  # Convertim în string
            "myLosses": str(myStatistic.losses),  # Convertim în string
            "otherLosses": str(otherStatistic.losses),  # Convertim în string
            "myDraws": str(myStatistic.draws),  # Convertim în string
            "otherDraws": str(otherStatistic.draws),  # Convertim în string
            "myTotalMatches": str(myStatistic.games_played),  # Convertim în string
            "otherTotalMatches": str(otherStatistic.games_played), # Convertim în string
            "caller_profile_picture": caller_base64,
            "requested_profile_picture": requested_user_base64
        }
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
