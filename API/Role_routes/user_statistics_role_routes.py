from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from API.Authentication.jwt_handler import get_user_by_id
from API.Schemas.statisticModels import User_Statistic_Response
from API.Role_models.userModel import UserGet
from API.security import manager
from storage.database import UserStatistic, Roles
from storage.db_utils import get_db
from sqlalchemy import and_

user_statistics_role_router = APIRouter(prefix="/role/user_statistics", tags=["Role-User-Statistics"])


@user_statistics_role_router.get("/get")
def get_user_statistic(
        data: UserGet,
        db: Session = Depends(get_db),
        user_id: str = Depends(manager)
):

    user = get_user_by_id(user_id, db)
    user_role_data = db.query(Roles).filter(and_(Roles.name == user.role)).first()
    if user_role_data.user_get:
        statistic = db.query(UserStatistic).filter(and_(UserStatistic.userEmail == data.email)).first()
        return User_Statistic_Response(
            games_played=statistic.games_played,
            draws=statistic.draws,
            losses=statistic.losses,
            points=statistic.points
        )
    else:
        raise HTTPException(status_code=400, detail="You dont have the right access!")
