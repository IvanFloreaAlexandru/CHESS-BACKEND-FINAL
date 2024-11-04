import datetime
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import and_
from sqlalchemy.orm import Session

from API.Authentication.jwt_handler import get_user_by_id
from API.Schemas.tRegistrationModels import Tournament_Registration_Create, Tournament_Registration_Response, \
    Tournament_Registration_Update, Tournament_Registration_Delete
from API.security import manager
from storage.database import TournamentRegistration
from storage.db_utils import get_db

tournament_registrations_router = APIRouter(prefix="/tournament_registrations", tags=["Tournament_registrations"])

#TODO de verificat intai daca tournament_id-ul este valid ca sa nu mai dea throw la toate erorile in consola

@tournament_registrations_router.post("/")
def create_tournament_registration(
        data: Tournament_Registration_Create,
        db: Session = Depends(get_db),
        user_id: str = Depends(manager)
) -> Tournament_Registration_Response:

    user = get_user_by_id(user_id, db)
    registration = db.query(TournamentRegistration).filter(
        and_(
            TournamentRegistration.userEmail == user.email,
            TournamentRegistration.tournament_id == data.tournament_id
        )
    ).first()

    if registration:
        raise HTTPException(status_code=404, detail="TRCE1")

    db_registration = TournamentRegistration(
        registration_id=str(uuid.uuid4()),
        tournament_id=data.tournament_id,
        userEmail=user.email,
        registration_date=datetime.datetime.now(),
        points_scored=0
    )
    db.add(db_registration)
    db.commit()
    db.refresh(db_registration)

    return Tournament_Registration_Response(
        registration_id=db_registration.registration_id,
        tournament_id=db_registration.tournament_id,
        userEmail=db_registration.userEmail,
        registration_date=db_registration.registration_date,
        points_scored=db_registration.points_scored
    )


@tournament_registrations_router.get("/get")
def get_tournament_registration(
        data: Tournament_Registration_Create,
        db: Session = Depends(get_db),
        user_id: str = Depends(manager)) -> Tournament_Registration_Response:
    user = get_user_by_id(user_id, db)

    registration = db.query(TournamentRegistration).filter(
        and_(
            TournamentRegistration.userEmail == user.email,
            TournamentRegistration.tournament_id == data.tournament_id)
    ).first()

    if not registration:
        raise HTTPException(status_code=404, detail="TRCE2")

    return Tournament_Registration_Response(
        registration_id=registration.registration_id,
        tournament_id=registration.tournament_id,
        userEmail=registration.userEmail,
        registration_date=registration.registration_date,
        points_scored=registration.points_scored
    )


@tournament_registrations_router.put("/put")
def update_tournament_registration(
        data: Tournament_Registration_Update,
        db: Session = Depends(get_db),
        user_id: str = Depends(manager)) -> Tournament_Registration_Response:

    user = get_user_by_id(user_id, db)
    db_registration = db.query(TournamentRegistration).filter(
        and_(
            TournamentRegistration.userEmail == user.email,
            TournamentRegistration.registration_id == data.registration_id
        )
    ).first()

    '''# and_ elimina eroarea Expected type 'ColumnElement[bool] | _HasClauseElement | SQLCoreOperations[bool] | 
    ExpressionElementRole[bool] | () -> ColumnElement[bool] | LambdaElement', got 'bool' instead 
    #  Inspection info:
    # Reports type errors in function call expressions, targets, and return values. In a dynamically typed language,
     this is possible in a limited number of cases.
    # Types of function parameters can be specified in docstrings or in Python 3 function annotations.
    '''

    if not db_registration:
        raise HTTPException(status_code=404, detail="TRCE2")

    db_registration.points_scored = data.points_scored

    db.commit()

    return Tournament_Registration_Response(
        registration_id=db_registration.registration_id,
        tournament_id=db_registration.tournament_id,
        userEmail=db_registration.userEmail,
        registration_date=db_registration.registration_date,
        points_scored=db_registration.points_scored
    )


@tournament_registrations_router.delete("/delete")
def delete_tournament_registration(
        data: Tournament_Registration_Delete,
        db: Session = Depends(get_db),
        user_id: str = Depends(manager)):
    user = get_user_by_id(user_id, db)
    registration = db.query(TournamentRegistration).filter(
        and_(
            TournamentRegistration.userEmail == user.email,
            TournamentRegistration.registration_id == data.registration_id)
    ).first()

    if not registration:
        raise HTTPException(status_code=404, detail="TRCE2")

    db.delete(registration)
    db.commit()
    return {"message": "Tournament Registration deleted successfully"}
