from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from API.Authentication.jwt_handler import get_user_by_id
from API.Schemas.statisticModels import User_Statistic_Response
from API.security import manager
from storage.database import UserStatistic
from storage.db_utils import get_db
from sqlalchemy import and_

user_statistics_router = APIRouter(prefix="/user_statistics", tags=["User Statistics"])


'''@user_statistics_router.post("/")
def create_user_statistic(
        db: Session = Depends(get_db),
        user_id: str = Depends(manager)):

    user = get_user_by_id(user_id, db)
    userFound = db.query(User_Statistic).filter(and_(User_Statistic.userEmail == user.email)).first()
    if not userFound:
        db_statistic = User_Statistic(
            user_statistics_id=str(uuid.uuid4()),
            userEmail=user.email,
            games_played=0,
            draws=0,
            losses=0,
            points=0
        )
        return User_Statistic_Response(
            user_statistics_id=db_statistic.user_statistics_id,
            userEmail=db_statistic.userEmail,
            games_played=db_statistic.games_played,
            draws=db_statistic.draws,
            losses=db_statistic.losses,
            points=db_statistic.points
        )
    else:
        raise HTTPException(status_code=404, detail="USTE1")'''


@user_statistics_router.put("/put")
def update_user_statistic(
        data: User_Statistic_Response,
        db: Session = Depends(get_db),
        user_id: str = Depends(manager)
):
    user = get_user_by_id(user_id, db)
    if not user:
        raise HTTPException(status_code=404, detail="")

    statistic = db.query(UserStatistic).filter(and_(user.email == UserStatistic.userEmail)).first()
    if not statistic:
        raise HTTPException(status_code=401, detail="USTE2")
    statistic.user_statistics_id = statistic.user_statistics_id,
    statistic.userEmail = statistic.userEmail
    statistic.games_played = data.games_played
    statistic.draws = data.draws
    statistic.losses = data.losses
    statistic.points = data.points

    db.commit()
    db.refresh(statistic)
    return User_Statistic_Response(
        games_played=statistic.games_played,
        draws=statistic.draws,
        losses=statistic.losses,
        points=statistic.points,
        wins=statistic.wins)


@user_statistics_router.get("/get")
def get_user_statistic(
        db: Session = Depends(get_db),
        user_id: str = Depends(manager)
):
    user = get_user_by_id(user_id, db)
    if not user:
        raise HTTPException(status_code=404, detail="")

    statistic = db.query(UserStatistic).filter(and_(UserStatistic.userEmail == user.email)).first()
    if not statistic:
        raise HTTPException(status_code=404, detail="UST2")
    return User_Statistic_Response(
        games_played=statistic.games_played,
        wins=statistic.wins,
        draws=statistic.draws,
        losses=statistic.losses,
        points=statistic.points
    )


'''@user_statistics_router.delete("/delete")
def delete_user_statistic(
        db: Session = Depends(get_db),
        user_id: str = Depends(manager)):

    user = get_user_by_id(user_id, db)

    statistic = db.query(User_Statistic).filter(and_(User_Statistic.userEmail == user.email)).first()
    if not statistic:
        raise HTTPException(status_code=404, detail="UST2")

    db.delete(statistic)
    db.commit()

    return {"message": "User Statistic deleted successfully"}'''
