from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from .interfaces import AbctractUserRepository
from ...models import User, BlacklistToken


class UserRepository(AbctractUserRepository):
    def __init__(self, db: Session):
        self.db = db
    
    def create_user(self, email, hashed_password):

        try:
            existing = self.db.query(User).filter(User.email == email).first()
            if existing:
                raise HTTPException(status_code=400, detail="Email already registered")
            
            user = User(email=email, hashed_password=hashed_password)
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            return user
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=400, detail="Email already registered (constraint)")
        except SQLAlchemyError:
            self.db.rollback()
            raise HTTPException(status_code=500, detail="Database error")

    def get_user_by_email(self, email):
        user = self.db.query(User).filter(User.email == email).first()
        return user
    
    def add_blacklist(self, token: str):
        try:
            token = BlacklistToken(token=token)
            self.db.add(token)
            self.db.commit()
        except SQLAlchemyError:
            self.db.rollback()
            raise HTTPException(status_code=500, detail="Failed to blacklist token")
        
    def is_blacklisted(self, token: str) -> bool:
        return self.db.query(BlacklistToken).filter_by(token=token).first() is not None
    
    def update(self, user):
        try:
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            return user
        except SQLAlchemyError:
            self.db.rollback()
            raise HTTPException(status_code=500, detail="Database update error")
