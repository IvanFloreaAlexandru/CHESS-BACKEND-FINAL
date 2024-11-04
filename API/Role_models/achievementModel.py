from pydantic import BaseModel
from typing import Optional

class AchievementModifier(BaseModel):
    wins: Optional[dict] = {
        "OneWin": 0,
        "FiveWins": 0,
        "TenWins": 0,
        "TwentyFiveWins": 0,
        "FiftyWins": 0,
        "HundredWins": 0,
        "OneVsBotWin": 0,
        "FiveVsBotWins": 0,
        "TenVsBotWins": 0,
        "TwentyFiveVsBotWins": 0,
        "FiftyVsBotWins": 0,
        "HundredVsBotWins": 0,
    }
    loses: Optional[dict] = {
        "OneLose": 0,
        "FiveLooses": 0,
        "TenLooses": 0,
        "TwentyFiveLooses": 0,
        "FiftyLooses": 0,
        "HundredLooses": 0,
        "OneVsBotLose": 0,
        "FiveVsBotLooses": 0,
        "TenVsBotLooses": 0,
        "TwentyFiveVsBotLooses": 0,
        "FiftyVsBotLooses": 0,
        "HundredVsBotLooses": 0,
    }
    FirstCompletedPuzzle: Optional[int] = 0
    outcome: Optional[str] = ""
