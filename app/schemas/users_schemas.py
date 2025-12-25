from pydantic import BaseModel, EmailStr


class UserIn(BaseModel):
    email:EmailStr
    password:str

class UserOut(BaseModel):
    email: EmailStr
    display_name: str | None = None
    
class AccessRefreshOut(BaseModel):
    refresh: str
    access: str
    
class RefreshIn(BaseModel):
    refresh: str
    
class Me(BaseModel):
    email: EmailStr
    display_name: str | None
    time_zone: str | None

class ProfilUpdateIn(BaseModel):
    display_name: str | None = None
    time_zone: str | None = None
    
class ProfilUpdateOut(ProfilUpdateIn):
    id: int
    email: EmailStr
    display_name: str | None = None
    


    
