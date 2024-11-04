import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import and_
from sqlalchemy.orm import Session

from API.Authentication.jwt_handler import get_user_by_id
from API.Schemas.tournamentModels import TournamentCreate, TournamentUpdate
from API.Schemas.tournamentModels import TournamentResponse
from API.security import manager
from storage.database import Tournament
from storage.db_utils import get_db

tournament_router = APIRouter(prefix="/tournaments", tags=["Tournaments"])


@tournament_router.post("/")
def create_tournament(
        data: TournamentCreate,
        db: Session = Depends(get_db),
        user_id: str = Depends(manager)
            ) -> TournamentResponse:

    tournament_id = str(uuid.uuid4())
    user = get_user_by_id(user_id, db)
    if not user:
        raise HTTPException(status_code=404, detail="")

    userFound = db.query(Tournament).filter(and_(Tournament.organizerEmail == user.email)).first()
    if not userFound:
        '''if tournament.start_date - tournament.end_date < 2 ore raise error
        sau if tournament.start_date - datetime.datime.now < 30 minute raise error'''

        db_tournament = Tournament(
            tournament_id=tournament_id,
            name=data.name,
            start_date=data.start_date,
            end_date=data.end_date,
            time_control=data.time_control,
            type=data.type,
            entry_fee=data.entry_fee,
            prize_pool=0,
            organizerEmail=user.email,
            winnersEmail=None
        )
        db.add(db_tournament)
        db.commit()
        db.refresh(db_tournament)

        return TournamentResponse(
            tournament_id=db_tournament.tournament_id,
            name=db_tournament.name,
            start_date=db_tournament.start_date,
            end_date=db_tournament.end_date,
            time_control=db_tournament.time_control,
            type=db_tournament.type,
            entry_fee=db_tournament.entry_fee,
            prize_pool=db_tournament.prize_pool,
            organizerEmail=db_tournament.organizerEmail,
            winnersEmail=db_tournament.winnersEmail
        )
    else:
        raise HTTPException(status_code=404, detail="TCE1")

# TODO solve errors from create tournament and role-update-tournament


@tournament_router.get("/get")
def get_tournament(
        db: Session = Depends(get_db),
        user_id: str = Depends(manager)
                ) -> TournamentResponse:

    user = get_user_by_id(user_id, db)
    if not user:
        raise HTTPException(status_code=404, detail="")

    userTournamentData = db.query(Tournament).filter(and_(Tournament.organizerEmail == user.email)).first()
    if userTournamentData:
        tournament = db.query(Tournament).filter(
            and_(
                Tournament.tournament_id == userTournamentData.tournament_id)
        ).first()
        if tournament is None:
            raise HTTPException(status_code=404, detail="TCE2")
        else:
            return TournamentResponse(
                tournament_id=userTournamentData.tournament_id,
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


@tournament_router.put("/put")
def update_tournament(
        data: TournamentUpdate,
        db: Session = Depends(get_db),
        user_id: str = Depends(manager)
                      ) -> TournamentResponse:

    user = get_user_by_id(user_id, db)
    if not user:
        raise HTTPException(status_code=404, detail="")

    userTournamentData = db.query(Tournament).filter(and_(Tournament.organizerEmail == user.email)).first()
    if not userTournamentData:
        raise HTTPException(status_code=404, detail="TCE2")
    tournament = db.query(Tournament).filter(and_(Tournament.tournament_id == userTournamentData.tournament_id)).first()
    if tournament is None:
        raise HTTPException(status_code=404, detail="Tournament not found")

    db.commit()
    db.refresh(tournament)
    return TournamentResponse(
        tournament_id=userTournamentData.tournament_id,
        name=data.name,
        start_date=userTournamentData.start_date,
        end_date=data.end_date,
        time_control=userTournamentData.time_control,
        type=userTournamentData.type,
        entry_fee=userTournamentData.entry_fee,
        prize_pool=userTournamentData.prize_pool,
        organizerEmail=user.email,
        winnersEmail=data.winnersEmail
    )

# Admin


@tournament_router.delete("/delete")
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
