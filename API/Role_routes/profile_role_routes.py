import uuid
from io import BytesIO

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from PIL import Image

from API.Authentication.jwt_handler import get_user_by_id
from API.security import manager
from storage.database import Session, Profile
from storage.db_utils import get_db
from fastapi.responses import FileResponse

profile_role_router = APIRouter(prefix="/roles", tags=["Profile Picture"])

IMAGEDIR = "D:/Programare/Pycharm/ChessModify/storage/Avatars/"


#TODO update and delete, get error if it is not created, get all basic images and set for each user the default photo

@profile_role_router.get("/get_picture")
def get_profile_picture(
        db: Session = Depends(get_db),
        user_id: str = Depends(manager)):
    user = get_user_by_id(user_id, db)
    photo = db.query(Profile).filter(user.email == Profile.userEmail).first()
    path = f"{IMAGEDIR}{photo.name}"

    return FileResponse(path)


@profile_role_router.post("/upload/")
async def create_upload_file(db: Session = Depends(get_db),
                             user_id: str = Depends(manager),
                             file: UploadFile = File(...)):
    user = get_user_by_id(user_id, db)
    photo = db.query(Profile).filter(user.email == Profile.userEmail).first()
    if photo:
        return HTTPException(status_code=400, detail="Already has a picture")

    photo_id = str(uuid.uuid4())
    file.filename = f"{photo_id}.jpg"
    allowed_formats = ["image/png", "image/jpeg", "image/jpg"]
    min_width, min_height = 90, 90
    max_width, max_height = 128, 128

    if file.content_type not in allowed_formats:
        raise HTTPException(status_code=415, detail="Invalid photo format. Allowed formats: PNG, JPEG, JPG")

    contents = await file.read()
    image = Image.open(BytesIO(contents))
    width, height = image.size

    if width < min_width or height < min_height or width > max_width or height > max_height:
        raise HTTPException(status_code=400, detail=f"Image dimensions must be between {min_width}x{min_height}and "
                                                    f"{max_width}x{max_height} pixels.")

    with open(f"{IMAGEDIR}{file.filename}", "wb") as f:
        f.write(contents)

    profile = Profile(
        picture_id=photo_id,
        name=photo_id + ".jpg",
        userEmail=user.email)

    db.add(profile)
    db.commit()
    db.refresh(Profile)
    return {"filename": file.filename}

# poza default si blocarea punerii unei poze custom
#TODO acesta poate doar sa preia profilul acestuia si sa modifice poza daca e de ceva ( sa puna una basic )
#TODO achievements and badges, profile ( poza, descriere, badges, achievemens, history of bans/warns/mutes etc )
