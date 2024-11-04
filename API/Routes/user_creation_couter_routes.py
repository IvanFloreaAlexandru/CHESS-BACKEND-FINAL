from datetime import datetime, date
from fastapi import APIRouter, Depends

from API.security import manager
from storage.database import Session, User
from storage.db_utils import get_db

user_creation_router = APIRouter(tags=["User Creation Router"], prefix="/usersBy")


@user_creation_router.get("/lastDay")
def get_users_by_last_day_registration(
        db: Session = Depends(get_db),
        user_id: str = Depends(manager)):

    allUsers = db.query(User).all()
    counter = 0

    today = datetime.today()

    year = today.year
    month = today.month
    day = today.day

    specific_date = datetime(year, month, day)

    for user in allUsers:
        if isinstance(user.registration_date, date) and not isinstance(user.registration_date, datetime):
            user_registration_datetime = datetime.combine(user.registration_date, datetime.min.time())
        else:
            user_registration_datetime = user.registration_date

        if user_registration_datetime >= specific_date >= user_registration_datetime:
            counter += 1

    return {"count": counter}



