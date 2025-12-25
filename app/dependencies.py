from fastapi import Depends
from .database import SessionLocal
from sqlalchemy.orm import Session
from typing import Annotated
from fastapi.security import OAuth2PasswordBearer

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
db_dependency = Annotated[Session, Depends(get_db)]
        
    

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login/")

jwt_dependency = Annotated[str, Depends(oauth2_scheme)]
