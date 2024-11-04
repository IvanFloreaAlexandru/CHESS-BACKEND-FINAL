import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import and_
from sqlalchemy.orm import Session

from API.Authentication.jwt_handler import get_user_by_id
from API.Role_models.tournamentModels import GetTournament, TournamentResponse, TournamentUpdate
from API.security import manager
from storage.database import Tournament
from storage.db_utils import get_db

tournement_role_router = APIRouter(prefix="/roles/tournaments", tags=["Role-Tournaments"])


@tournement_role_router.get("/")
def get_tournament(
        data: GetTournament,
        db: Session = Depends(get_db),
        user_id: str = Depends(manager)
) -> TournamentResponse:
    user = get_user_by_id(user_id, db)
    if data.organizerEmail and data.name:
        userTournamentData = db.query(Tournament).filter(
            and_(Tournament.organizerEmail == data.organizerEmail, Tournament.name == data.name)).first()
        if userTournamentData:
            return TournamentResponse(
                name=userTournamentData.name,
                start_date=userTournamentData.start_date,
                end_date=userTournamentData.end_date,
                time_control=userTournamentData.time_control,
                type=userTournamentData.type,
                entry_fee=userTournamentData.entry_fee,
                prize_pool=userTournamentData.prize_pool,
                organizerEmail=user.email,
                winnersEmail=userTournamentData.winnersEmail
            )
        else:
            raise HTTPException(status_code=404, detail="TCE3")
    else:
        raise HTTPException(status_code=400, detail="One or more fields are empty.")


"""@tournement_role_router.put("/modify")
def update_tournament(
        modify_data: TournamentUpdate,
        db: Session = Depends(get_db),
        user_id: str = Depends(manager)
):
    user = get_user_by_id(user_id, db)
    TournamentData = db.query(Tournament).filter(
        and_(Tournament.organizerEmail == modify_data.organizerEmail, Tournament.name == modify_data.name)).first()
    if not TournamentData:
        raise HTTPException(status_code=404, detail="TCE2")
    if TournamentData.start_date > datetime.datetime.now():
        raise HTTPException(status_code=404, detail="You cant modify a tournament that is active!(has started)")
    TournamentData.name = modify_data.name
    TournamentData.start_date = modify_data.start_date
    TournamentData.end_date = modify_data.end_date
    TournamentData.time_control = modify_data.time_control
    TournamentData.type = modify_data.type
    TournamentData.winnersEmail = modify_data.winnersEmail
    TournamentData.prize_pool = modify_data.prize_pool
    db.commit()
    db.refresh(TournamentData)
    return {"message":"You have succesfully modified the tournament!"}"""


# Admin

# de implementat atunci cand un jucator este banat sau are nume urat, tournamentul nu a inceput
@tournement_role_router.delete("/delete")  # pt jucatori banati sau nume urate
def delete_tournament(
        db: Session = Depends(get_db),
        user_id: str = Depends(manager)):
    user = get_user_by_id(user_id, db)
    tournament = db.query(Tournament).filter(and_(Tournament.organizerEmail == user.email)).first()
    if tournament is None:
        raise HTTPException(status_code=404, detail="TCE2")

    db.delete(tournament)
    db.commit()
    return {"message": "Tournament deleted successfully"}
    # TODO sa se verifice atunci cand un tournament