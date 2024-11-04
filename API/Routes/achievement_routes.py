from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import and_

from API.Authentication.jwt_handler import get_user_by_id
from API.Role_models.achievementModel import AchievementModifier
from API.security import manager
from storage.database import Session, Achievements, User
from storage.db_utils import get_db

achievement_router = APIRouter(tags=["Achievements"], prefix="/achievements")


@achievement_router.get("/get_all_achievements")
def get_all_achievements(
        db: Session = Depends(get_db),
        user_id: str = Depends(manager)
):
    user = get_user_by_id(user_id, db)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    achievements = db.query(Achievements).filter(and_(User.user_id == Achievements.user_id),
                                                 User.user_id == user_id).first()
    if not achievements:
        raise HTTPException(status_code=404, detail="Achievements not found")

    # Definește țintele pentru fiecare realizare
    achievement_targets = {
        "OneWin": 1, "FiveWins": 5, "TenWins": 10, "TwentyFiveWins": 25, "FiftyWins": 50, "HundredWins": 100,
        "OneLose": 1, "FiveLooses": 5, "TenLooses": 10, "TwentyFiveLooses": 25, "FiftyLooses": 50, "HundredLooses": 100,
        "OneWinStreak": 1, "FiveWinStreak": 5, "TenWinStreak": 10, "TwentyFiveWinStreak": 25, "FiftyWinStreak": 50, "HundredWinStreak": 100,
        "OneLoseStreak": 1, "FiveLoseStreak": 5, "TenLoseStreak": 10, "TwentyFiveLoseStreak": 25, "FiftyLoseStreak": 50, "HundredLoseStreak": 100,
        "OneVsBotWin": 1, "FiveVsBotWins": 5, "TenVsBotWins": 10, "TwentyFiveVsBotWins": 25, "FiftyVsBotWins": 50, "HundredVsBotWins": 100,
        "OneVsBotLose": 1, "FiveVsBotLooses": 5, "TenVsBotLooses": 10, "TwentyFiveVsBotLooses": 25, "FiftyVsBotLooses": 50, "HundredVsBotLooses": 100,
        "FirstCompletedPuzzle": 1
    }

    achievements_dict = {}
    for achievement, target in achievement_targets.items():
        current_value = getattr(achievements, achievement, 0)
        percentage = min((current_value / target) * 100, 100.0)
        achievements_dict[achievement] = {
            "value": current_value,
            "percentage": percentage
        }

    return achievements_dict


@achievement_router.put("/achievement_updater")
def achievement_updater(
        data: AchievementModifier,
        db: Session = Depends(get_db),
        user_id: str = Depends(manager)
):
    user = get_user_by_id(user_id, db)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    achievements = db.query(Achievements).filter(and_(User.user_id == Achievements.user_id),
                                                 User.user_id == user_id).first()
    if not achievements:
        raise HTTPException(status_code=404, detail="Achievements not found")

    achievement_targets = {
        "OneWin": 1, "FiveWins": 5, "TenWins": 10, "TwentyFiveWins": 25, "FiftyWins": 50, "HundredWins": 100,
        "OneLose": 1, "FiveLooses": 5, "TenLooses": 10, "TwentyFiveLooses": 25, "FiftyLooses": 50, "HundredLooses": 100,
        "OneWinStreak": 1, "FiveWinStreak": 5, "TenWinStreak": 10, "TwentyFiveWinStreak": 25, "FiftyWinStreak": 50, "HundredWinStreak": 100,
        "OneLoseStreak": 1, "FiveLoseStreak": 5, "TenLoseStreak": 10, "TwentyFiveLoseStreak": 25, "FiftyLoseStreak": 50, "HundredLoseStreak": 100,
        "OneVsBotWin": 1, "FiveVsBotWins": 5, "TenVsBotWins": 10, "TwentyFiveVsBotWins": 25, "FiftyVsBotWins": 50, "HundredVsBotWins": 100,
        "OneVsBotLose": 1, "FiveVsBotLooses": 5, "TenVsBotLooses": 10, "TwentyFiveVsBotLooses": 25, "FiftyVsBotLooses": 50, "HundredVsBotLooses": 100,
        "FirstCompletedPuzzle": 1
    }

    # Update wins
    for win_type, count in data.wins.items():
        if count > 0:
            current_value = getattr(achievements, win_type, 0)
            new_value = min(current_value + count, achievement_targets[win_type])
            setattr(achievements, win_type, new_value)
            print(f"Updated {win_type}: {current_value} -> {new_value}")

    # Update loses
    for lose_type, count in data.loses.items():
        if count > 0:
            current_value = getattr(achievements, lose_type, 0)
            new_value = min(current_value + count, achievement_targets[lose_type])  # Limitează actualizarea
            setattr(achievements, lose_type, new_value)
            print(f"Updated {lose_type}: {current_value} -> {new_value}")

    # Update streaks only if outcome is win or lose
    if data.outcome == "lose":
        achievements.CurrentWinStreak = 0
        update_lose_streaks(data, achievements)
    elif data.outcome == "win":
        achievements.CurrentLoseStreak = 0
        update_win_streaks(data, achievements)
    else:
        print("Outcome is not win or lose; no changes to streaks.")

    db.commit()
    db.refresh(achievements)
    print(f"Achievements after update: {achievements}")

    return achievements


def update_win_streaks(data, achievements):
    achievements.OneWinStreak = min(achievements.CurrentWinStreak, 1)
    achievements.FiveWinStreak = min(achievements.CurrentWinStreak, 5)
    achievements.TenWinStreak = min(achievements.CurrentWinStreak, 10)
    achievements.TwentyFiveWinStreak = min(achievements.CurrentWinStreak, 25)
    achievements.FiftyWinStreak = min(achievements.CurrentWinStreak, 50)
    achievements.HundredWinStreak = min(achievements.CurrentWinStreak, 100)

    return (
        achievements.OneWinStreak,
        achievements.FiveWinStreak,
        achievements.TenWinStreak,
        achievements.TwentyFiveWinStreak,
        achievements.FiftyWinStreak,
        achievements.HundredWinStreak
    )


def update_lose_streaks(data, achievements):
    current_lose_streak = achievements.CurrentLoseStreak

    if data.outcome == "lose":
        current_lose_streak += 1
    else:
        current_lose_streak = 0

    achievements.CurrentLoseStreak = current_lose_streak
    achievements.OneLoseStreak = min(current_lose_streak, 1)
    achievements.FiveLoseStreak = min(current_lose_streak, 5)
    achievements.TenLoseStreak = min(current_lose_streak, 10)
    achievements.TwentyFiveLoseStreak = min(current_lose_streak, 25)
    achievements.FiftyLoseStreak = min(current_lose_streak, 50)
    achievements.HundredLoseStreak = min(current_lose_streak, 100)

    return (
        achievements.OneLoseStreak,
        achievements.FiveLoseStreak,
        achievements.TenLoseStreak,
        achievements.TwentyFiveLoseStreak,
        achievements.FiftyLoseStreak,
        achievements.HundredLoseStreak
    )