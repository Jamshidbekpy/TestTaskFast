from abc import ABC, abstractmethod
from ...schemas.users_schemas import UserIn, UserOut, AccessRefreshOut, Me, ProfilUpdateOut

class AbctractUserService(ABC):
    @abstractmethod
    def register(self, user_in:UserIn) -> UserOut:
        pass
    
    @abstractmethod
    def login(self, user_in:UserIn) -> AccessRefreshOut:
        pass
    
    @abstractmethod
    def refresh(self, refresh_token: str) -> dict:
        pass
    
    @abstractmethod
    def logout(self, token: str) -> dict:
        pass
    
    @abstractmethod
    def me(self, access_token: str) -> Me:
        pass
    
    @abstractmethod
    def update(self, access_token: str) -> ProfilUpdateOut:
        pass
    