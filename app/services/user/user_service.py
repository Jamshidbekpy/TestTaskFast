from fastapi import HTTPException
from .interfaces import AbctractUserService
from ...schemas.users_schemas import (
    UserIn, UserOut, AccessRefreshOut, Me, ProfilUpdateOut, ProfilUpdateIn
)
from ...repository.user.user_repo import UserRepository
from ...utils.password import hash_password, verify_password
from ...utils.jwt import create_access_token, create_refresh_token, decode_token


class UserService(AbctractUserService):
    def __init__(self, repo: UserRepository):
        self.repo = repo
    
    def register(self, user_in: UserIn) -> UserOut:
        hashed_password = hash_password(user_in.password)
        user = self.repo.create_user(email=user_in.email, hashed_password=hashed_password)
        return UserOut(email=user.email)
    
    def login(self, user_in: UserIn) -> AccessRefreshOut:
        user = self.repo.get_user_by_email(user_in.email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if not verify_password(user_in.password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Invalid password")
        
        payload = {"sub": str(user.id), "email": user.email}
        access_token = create_access_token(payload)
        refresh_token = create_refresh_token(payload)
        
        return AccessRefreshOut(refresh=refresh_token, access=access_token)
        
    def refresh(self, refresh_token: str) -> dict:
        if self.repo.is_blacklisted(refresh_token):
            raise HTTPException(status_code=401, detail="Token blacklisted")

        payload = decode_token(refresh_token)
        user_email = payload.get("email")
        if not user_email:
            raise HTTPException(status_code=401, detail="Invalid token payload")

        new_access_token = create_access_token({"email": user_email})
        return {"access": new_access_token}
        
    def logout(self, token: str) -> dict:
        if self.repo.is_blacklisted(token):
            raise HTTPException(status_code=400, detail="Token already blacklisted")
        self.repo.add_blacklist(token)
        return {"message": "Successfully logged out"}
    
    def me(self, access_token: str) -> Me:
        payload = decode_token(access_token)
        user_email = payload.get("email")
        if not user_email:
            raise HTTPException(status_code=401, detail="Invalid token payload")

        user = self.repo.get_user_by_email(user_email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return Me(email=user.email, display_name=user.display_name or "", time_zone=user.time_zone or "")
        
    def update(self, access_token: str, user_in: ProfilUpdateIn) -> ProfilUpdateOut:
        payload = decode_token(access_token)
        user_email = payload.get("email")
        if not user_email:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        
        user = self.repo.get_user_by_email(user_email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user.display_name = user_in.display_name
        user.time_zone = user_in.time_zone
        
        user = self.repo.update(user=user)


        return ProfilUpdateOut(id=user.id, display_name=user.display_name, time_zone=user.time_zone)
    


