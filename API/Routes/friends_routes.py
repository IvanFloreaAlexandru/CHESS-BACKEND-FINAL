import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import and_
from sqlalchemy.orm import Session

from API.Authentication.jwt_handler import get_user_by_id
from API.security import manager
from API.Schemas.friendModels import FriendUpdate, FriendCreateOrDelete
from API.Schemas.friendModels import FriendResponse
from storage.database import Friends, User
from storage.db_utils import get_db
friends_router = APIRouter(prefix="/friends", tags=["Friends"])


@friends_router.post("/", response_model=FriendResponse)
def create_friendship(
        data: FriendCreateOrDelete,
        db: Session = Depends(get_db),
        user_id: str = Depends(manager)

) -> FriendResponse:

    user = get_user_by_id(user_id, db)
    if not user:
        raise HTTPException(status_code=404, detail="")

    friend_found = db.query(User).filter(User.email == data.friendEmail).first()
    if not friend_found:
        raise HTTPException(status_code=404, detail="FCE1")
    if not data.friendEmail:
        raise HTTPException(status_code=400, detail="FCE2")

    friendship_exists = db.query(Friends).filter(
        and_(
            Friends.userEmail == user.email,
            Friends.friendEmail == data.friendEmail
        )
    ).first()

    if friendship_exists:
        raise HTTPException(status_code=400, detail="FCE3")

    db_friendship = Friends(
        friendship_id=str(uuid.uuid4()),
        userEmail=user.email,
        friendEmail=data.friendEmail,
        status="Pending"
    )
    db.add(db_friendship)
    db.commit()
    db.refresh(db_friendship)

    return FriendResponse(
        friendship_id=db_friendship.friendship_id,
        userEmail=db_friendship.userEmail,
        friendEmail=db_friendship.friendEmail,
        status=db_friendship.status
    )


@friends_router.get("/get", response_model=List[FriendResponse])
def get_friend_requests(
        db: Session = Depends(get_db),
        user_id: str = Depends(manager)
) -> List[FriendResponse]:

    user = get_user_by_id(user_id, db)
    if not user:
        raise HTTPException(status_code=404, detail="")

    friend_requests = db.query(Friends).filter(
        and_(Friends.userEmail == user.email)).all()

    if not friend_requests:
        return []

    response = []
    for friend_request in friend_requests:
        response.append(FriendResponse(
            friendship_id=friend_request.friendship_id,
            userEmail=user.email,
            friendEmail=friend_request.friendEmail,
            status=friend_request.status
        ))

    return response


@friends_router.put("/update")
def update_friendship_status(
        data: FriendUpdate,
        db: Session = Depends(get_db),
        user_id: str = Depends(manager)
) -> FriendResponse:

    user = get_user_by_id(user_id, db)
    if not user:
        raise HTTPException(status_code=404, detail="")

    db_friendship = db.query(Friends).filter(
        and_(
            Friends.userEmail == user.email,
            Friends.friendEmail == data.friendEmail)
    ).first()

    if db_friendship:
        db_friendship.status = data.status
        db.commit()
        db.refresh(db_friendship)
        return FriendResponse(
            friendship_id=db_friendship.friendship_id,
            userEmail=db_friendship.userEmail,
            friendEmail=db_friendship.friendEmail,
            status=db_friendship.status
        )
    else:
        raise HTTPException(status_code=404, detail="FCE2")


@friends_router.delete("/delete")
def delete_friendship(
        data: FriendCreateOrDelete,
        db: Session = Depends(get_db),
        user_id: str = Depends(manager)
                      ):

    user = get_user_by_id(user_id, db)
    if not user:
        raise HTTPException(status_code=404, detail="")

    db_friendship = db.query(Friends).filter(
        and_(Friends.userEmail == user.email,
             data.friendEmail == Friends.friendEmail)
    ).first()

    if db_friendship:
        db.delete(db_friendship)
        db.commit()
        return {"message": "Friend request deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="FCE2")
