from collections import defaultdict
from datetime import datetime, date, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy import and_, or_

from API.security import manager
from storage.database import Session, User, Game
from storage.db_utils import get_db

leaderboard_router = APIRouter(tags=["LeaderBoards"])

# TODO send back the actual place of the player that accessed the endpoint


@leaderboard_router.get("/top100/byLastDay")
def get_leaderboard(
        db: Session = Depends(get_db),
        user_id: str = Depends(manager),
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=0, le=1000)
):
    start_of_day = datetime.combine(date.today(), datetime.min.time())
    end_of_day = datetime.combine(date.today(), datetime.max.time())

    matches_count_by_user = defaultdict(int)

    all_users = db.query(User).all()

    for eachUser in all_users:
        matches_count = db.query(Game).filter(
            and_(
                or_(Game.white_player == eachUser.email, Game.black_player == eachUser.email),
                Game.end_date_time >= start_of_day,
                Game.end_date_time <= end_of_day
            )
        ).count()

        matches_count_by_user[eachUser.email] = matches_count

    sorted_users = sorted(matches_count_by_user.items(), key=lambda x: x[1], reverse=True)

    leaderboard_slice = sorted_users[skip: skip + limit]

    return {"leaderboard": leaderboard_slice}


@leaderboard_router.get("/top100/byLastWeek")
def get_weekly_leaderboard(
        db: Session = Depends(get_db),
        user_id: str = Depends(manager),
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=0, le=1000)
):
    start_of_week = datetime.combine(date.today() - timedelta(days=date.today().weekday() + 7), datetime.min.time())
    end_of_week = datetime.combine(date.today(), datetime.max.time())
    matches_count_by_user = defaultdict(int)

    all_users = db.query(User).all()

    for eachUser in all_users:
        matches_count = db.query(Game).filter(
            and_(
                or_(Game.white_player == eachUser.email, Game.black_player == eachUser.email),
                Game.end_date_time >= start_of_week,
                Game.end_date_time <= end_of_week
            )
        ).count()

        matches_count_by_user[eachUser.email] = matches_count

    sorted_users = sorted(matches_count_by_user.items(), key=lambda x: x[1], reverse=True)

    leaderboard_slice = sorted_users[skip: skip + limit]

    return {"leaderboard": leaderboard_slice}


@leaderboard_router.get("/top100/byLastMonth")
def get_monthly_leaderboard(
        db: Session = Depends(get_db),
        user_id: str = Depends(manager),
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=0, le=1000)
):
    today = date.today()
    start_of_month = datetime(today.year, today.month, 1)
    end_of_month = datetime(today.year, today.month + 1, 1) - timedelta(days=1)
    matches_count_by_user = defaultdict(int)

    all_users = db.query(User).all()

    for eachUser in all_users:
        matches_count = db.query(Game).filter(
            and_(
                or_(Game.white_player == eachUser.email, Game.black_player == eachUser.email),
                Game.end_date_time >= start_of_month,
                Game.end_date_time <= end_of_month
            )
        ).count()

        matches_count_by_user[eachUser.email] = matches_count

    sorted_users = sorted(matches_count_by_user.items(), key=lambda x: x[1], reverse=True)

    leaderboard_slice = sorted_users[skip: skip + limit]

    return {"leaderboard": leaderboard_slice}


@leaderboard_router.get("/top100Wins/byLastDay")
def get_leaderboard(
        db: Session = Depends(get_db),
        user_id: str = Depends(manager),
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=0, le=1000)
):
    start_of_day = datetime.combine(date.today(), datetime.min.time())
    end_of_day = datetime.combine(date.today(), datetime.max.time())
    matches_count_by_user = defaultdict(int)

    all_users = db.query(User).all()

    for eachUser in all_users:
        won_matches = db.query(Game).filter(
            and_(
                or_(
                    and_(Game.white_player == eachUser.email, Game.result_white == "Won"),
                    and_(Game.black_player == eachUser.email, Game.result_black == "Won")
                ),
                Game.end_date_time >= start_of_day,
                Game.end_date_time <= end_of_day
            )
        ).count()

        matches_count_by_user[eachUser.email] = won_matches

    sorted_users = sorted(matches_count_by_user.items(), key=lambda x: x[1], reverse=True)

    leaderboard_slice = sorted_users[skip: skip + limit]

    return {"leaderboard": leaderboard_slice}


