from abc import ABC, abstractmethod

class AbctractUserRepository(ABC):
    @abstractmethod
    def create_user(self, email, hashed_password):
        pass
    
    @abstractmethod
    def get_user_by_email(self, email):
        pass
    @abstractmethod
    
    def add_blacklist(self, token):
        pass
    
    @abstractmethod   
    def is_blacklisted(self, token: str) -> bool:
        pass
    
    @abstractmethod
    def update(self, user):
        pass
    
    

