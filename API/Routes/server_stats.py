from fastapi import APIRouter, Depends

from API.Routes.user_creation_couter_routes import get_users_by_last_day_registration
from API.Websockets.Rooms import room_manager
from API.security import manager
from storage.database import Session, User, UserStatistic, Tournament
from storage.db_utils import get_db

server_stats_router = APIRouter(prefix="/server",tags=["Server Stats"])


@server_stats_router.get("/data")
def get_server_stats(
        user_id: str = Depends(manager),
        db: Session = Depends(get_db)

):
    # users (accounts created), owners, moderators, helpers, tournaments, games
    # TODO active connections and ongoing matches
    # total_users = db.query(User).count()
    allUsers = db.query(User).all()
    owner_count = 0
    moderator_count = 0
    helper_count = 0
    number_of_games_played = 0
    for user in allUsers:
        if user.role == "Owner":
            owner_count = owner_count + 1
        elif user.role == "Moderator":
            moderator_count = moderator_count + 1
        elif user.role == "Helper":
            helper_count = helper_count + 1
        user_stats = db.query(UserStatistic).filter(user.email == UserStatistic.userEmail).first()
        number_of_games_played = number_of_games_played + user_stats.games_played
    all_tournaments = db.query(Tournament).all()
    number_of_tournaments_ever = len(all_tournaments)
    number_of_active_users = room_manager.get_total_active_users()
    number_of_active_rooms = number_of_active_users // 2 if number_of_active_users > 0 else 0
    registrationUserNumber = get_users_by_last_day_registration(db=db,
                                                                user_id=user_id)
    return {"numberOfPlayersRegisteredToday": registrationUserNumber.get("count"),
            "numberOfGamesPlayed": number_of_games_played,
            "numberOfTournamentsEver": number_of_tournaments_ever,
            "numberOfActiveUsers": number_of_active_users,
            "numberOfActiveRooms": number_of_active_rooms}
