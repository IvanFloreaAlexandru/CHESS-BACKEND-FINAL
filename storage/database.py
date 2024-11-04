import datetime
import uuid

from dotenv import dotenv_values
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, DATE, Boolean, DECIMAL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

env_vars = dotenv_values(".env")

DATABASE_CREDENTIALS = env_vars.get("DATABASE_CREDENTIALS")
#DATABASE_URL = "postgresql://postgres:pZYOHFebkimonnAAMIgYnkZOvNcftLhV@junction.proxy.rlwy.net:37248/railway"

Base = declarative_base()
engine = create_engine(DATABASE_CREDENTIALS)


class User(Base):
    __tablename__ = 'users'

    user_id = Column(String(36), primary_key=True, default=str(uuid.uuid4()), unique=True)
    username = Column(String(50), nullable=False)
    password = Column(String(255), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    registration_date = Column(DATE, nullable=False)
    account_status = Column(String(36), default="Active")
    role = Column(String(36), ForeignKey("roles.name"), default="User")
    is_verified = Column(Boolean, default=False)
    warningsNumber = Column(Integer, nullable=False, default=0)
    cantTalk = Column(Boolean, default=False)
    twoFactor = Column(Boolean, default=False)
    twoFactorCode = Column(String(256), default=None)


class Roles(Base):
    __tablename__ = 'roles'

    role_id = Column(String(36), default=uuid.uuid4, unique=True)
    name = Column(String(36), primary_key=True, unique=True, default="")
    role_create = Column(Boolean, default=False)
    role_delete = Column(Boolean, default=False)
    role_level = Column(Integer, nullable=True)
    ban = Column(Boolean, default=False)
    unban = Column(Boolean, default=False)
    mute = Column(Boolean, default=False)
    unmute = Column(Boolean, default=False)
    warn = Column(Boolean, default=False)
    user_get = Column(Boolean, default=False)
    user_update = Column(Boolean, default=False)
    user_delete = Column(Boolean, default=False)
    user_settings_get = Column(Boolean, default=False)
    user_settings_update = Column(Boolean, default=False)
    user_statistics_get = Column(Boolean, default=False)
    user_statistics_update = Column(Boolean, default=False)
    friends_create = Column(Boolean, default=False)
    friends_get = Column(Boolean, default=False)
    friends_update = Column(Boolean, default=False)
    friends_delete = Column(Boolean, default=False)
    games_create = Column(Boolean, default=False)
    games_get = Column(Boolean, default=False)
    games_update = Column(Boolean, default=False)
    games_delete = Column(Boolean, default=False)
    moves_create = Column(Boolean, default=False)
    moves_get = Column(Boolean, default=False)
    moves_update = Column(Boolean, default=False)
    moves_delete = Column(Boolean, default=False)
    profile_create = Column(Boolean, default=False)
    profile_get = Column(Boolean, default=False)
    profile_update = Column(Boolean, default=False)
    profile_delete = Column(Boolean, default=False)
    tournament_registration_create = Column(Boolean, default=False)
    tournament_registration_get = Column(Boolean, default=False)
    tournament_registration_update = Column(Boolean, default=False)
    tournament_registration_delete = Column(Boolean, default=False)
    tournament_create = Column(Boolean, default=False)
    tournament_get = Column(Boolean, default=False)
    tournament_update = Column(Boolean, default=False)
    tournament_delete = Column(Boolean, default=False)


class Game(Base):
    __tablename__ = "games"

    game_id = Column(String(36), primary_key=True, default=uuid.uuid4, unique=True)
    end_date_time = Column(DateTime, nullable=True)
    result_white = Column(String(8), default=False)
    result_black = Column(String(8), default=True)
    white_player = Column(String(36), ForeignKey("users.email"))  # redenumire in white_player
    black_player = Column(String(36), ForeignKey("users.email"))  # redenumire in black_player


class Move(Base):
    __tablename__ = "moves"

    move_id = Column(String(36), primary_key=True, default=uuid.uuid4, unique=True)
    game_id = Column(String(36), ForeignKey("games.game_id"), nullable=False)
    moves = Column(String(512), default="")


class TournamentRegistration(Base):
    __tablename__ = "tournament_registrations"

    registration_id = Column(String(36), primary_key=True, nullable=False, default=uuid.uuid4, unique=True)
    tournament_id = Column(String(36), ForeignKey("tournaments.tournament_id"), nullable=False)
    userEmail = Column(String(100), ForeignKey("users.email"), nullable=False)
    registration_date = Column(DateTime, nullable=False, default=datetime)
    points_scored = Column(Integer, default=0)


class Tournament(Base):
    __tablename__ = "tournaments"

    tournament_id = Column(String(36), nullable=False, primary_key=True, default=uuid.uuid4, unique=True)
    name = Column(String(100))
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True)
    time_control = Column(Integer, nullable=False)  # Numarul de minute la meci
    type = Column(String(50))
    entry_fee = Column(Integer, nullable=True)
    prize_pool = Column(Integer, nullable=True)
    organizerEmail = Column(String(100), ForeignKey("users.email"), nullable=False)
    winnersEmail = Column(String(100), default=None, nullable=True)


class UserStatistic(Base):
    __tablename__ = "user_statistics"

    user_statistics_id = Column(String(36), primary_key=True, default=uuid.uuid4(), unique=True)
    userEmail = Column(String(100), ForeignKey("users.email", ondelete='CASCADE'), nullable=False)
    games_played = Column(Integer, default=0)
    wins = Column(Integer, default=0)
    draws = Column(Integer, default=0)
    losses = Column(Integer, default=0)
    points = Column(Integer, default=0)
    winrate = Column(DECIMAL(5, 2))


class UserSetting(Base):
    __tablename__ = "user_settings"

    user_setting_id = Column(String(36), default=uuid.uuid4(), primary_key=True, unique=True)
    userEmail = Column(String(100), ForeignKey("users.email", ondelete='CASCADE'))
    itemsPurchased = Column(String(255))
    settings = Column(String(255))


class Friends(Base):
    __tablename__ = "friends"

    friendship_id = Column(String(36), primary_key=True, default=uuid.uuid4, unique=True)
    userEmail = Column(String(100), ForeignKey("users.email"), nullable=False)
    friendEmail = Column(String(36), ForeignKey("users.email"), nullable=False)
    status = Column(String(20), default="pending")


class LookingForGames(Base):
    __tablename__ = "lookingforgame"

    looking_id = Column(String(36), primary_key=True, default=str(uuid.uuid4()), unique=True)
    userEmail = Column(String(100), ForeignKey("users.email"))
    gamemode = Column(String(36))


class RoomStoring(Base):
    __tablename__ = "roomstoring"

    room_id = Column(String(36), primary_key=True, unique=True)
    player1JWT = Column(String(256))
    player2JWT = Column(String(256))


class Profile(Base):
    __tablename__ = "profile"

    profile_id = Column(String(36), primary_key=True, unique=True, default=lambda: str(uuid.uuid4()))
    photoData = Column(String(64), nullable=True)
    userEmail = Column(String(100), ForeignKey("users.email"), nullable=False)
    description = Column(String(256), nullable=False, default="Hi! This is the basic description!")


class AdminLogs(Base):
    __tablename__ = "role_logs"
    log_id = Column(String(36), unique=True, primary_key=True, default=str(uuid.uuid4()))
    role_email = Column(String(100), ForeignKey("users.email"))
    user_email = Column(String(100), ForeignKey("users.email"))
    reason = Column(String(256))
    action = Column(String(256))
    date = Column(DATE, nullable=False)


class Achievements(Base):
    __tablename__ = "achievements"
    achievement_id = Column(String(36), unique=True, primary_key=True, default=str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey(User.user_id))
    OneWin = Column(Integer, default=0)
    FiveWins = Column(Integer, default=0)
    TenWins = Column(Integer, default=0)
    TwentyFiveWins = Column(Integer, default=0)
    FiftyWins = Column(Integer, default=0)
    HundredWins = Column(Integer, default=0)
    OneLose = Column(Integer, default=0)
    FiveLooses = Column(Integer, default=0)
    TenLooses = Column(Integer, default=0)
    TwentyFiveLooses = Column(Integer, default=0)
    FiftyLooses = Column(Integer, default=0)
    HundredLooses = Column(Integer, default=0)
    OneWinStreak = Column(Integer, default=0)
    FiveWinStreak = Column(Integer, default=0)
    TenWinStreak = Column(Integer, default=0)
    TwentyFiveWinStreak = Column(Integer, default=0)
    FiftyWinStreak = Column(Integer, default=0)
    HundredWinStreak = Column(Integer, default=0)
    OneLoseStreak = Column(Integer, default=0)
    FiveLoseStreak = Column(Integer, default=0)
    TenLoseStreak = Column(Integer, default=0)
    TwentyFiveLoseStreak = Column(Integer, default=0)
    FiftyLoseStreak = Column(Integer, default=0)
    HundredLoseStreak = Column(Integer, default=0)
    OneVsBotWin = Column(Integer, default=0)
    FiveVsBotWins = Column(Integer, default=0)
    TenVsBotWins = Column(Integer, default=0)
    TwentyFiveVsBotWins = Column(Integer, default=0)
    FiftyVsBotWins = Column(Integer, default=0)
    HundredVsBotWins = Column(Integer, default=0)
    OneVsBotLose = Column(Integer, default=0)
    FiveVsBotLooses = Column(Integer, default=0)
    TenVsBotLooses = Column(Integer, default=0)
    TwentyFiveVsBotLooses = Column(Integer, default=0)
    FiftyVsBotLooses = Column(Integer, default=0)
    HundredVsBotLooses = Column(Integer, default=0)
    FirstCompletedPuzzle = Column(Integer, default=0)
    CurrentWinStreak = Column(Integer, default=0)
    CurrentLoseStreak = Column(Integer, default=0)


Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()
user_role = session.query(Roles).filter_by(name="User").first()
if not user_role:
    default_user_role = Roles(
        name="User",
        role_level=0,
        role_create=False,
        role_delete=False,
        ban=False,
        unban=False,
        mute=False,
        unmute=False,
        warn=False,
        user_get=False,
        user_update=False,
        user_delete=False
    )
    session.add(default_user_role)
    session.commit()

session.commit()

# Administrator, Moderator, Premium user, User, logging actions for administrator and moderator
# Functionalitate de ban