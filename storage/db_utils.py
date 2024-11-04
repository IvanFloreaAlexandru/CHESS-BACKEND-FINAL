from sqlalchemy.orm import Session
from storage.database import Session


def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()
