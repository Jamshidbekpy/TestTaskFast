from fastapi import APIRouter
from ...dependencies import db_dependency, jwt_dependency
from ...schemas.users_schemas import UserIn, UserOut, AccessRefreshOut, RefreshIn, Me, ProfilUpdateIn, ProfilUpdateOut
from ...repository.user_repo.user_repo import UserRepository
from ...services.user_service.user_service import UserService

router = APIRouter(
    prefix="/auth"
)


@router.post("/register/", response_model=UserOut)
def register(user_in: UserIn, db:db_dependency):
    repo = UserRepository(db)
    service = UserService(repo)
    
    return service.register(user_in)


@router.post("/login/", response_model=AccessRefreshOut)
def login(user_in: UserIn, db:db_dependency):
    repo = UserRepository(db)
    service = UserService(repo)
    
    return service.login(user_in)

@router.post("/refresh/")
def refresh(refresh_token: RefreshIn, db:db_dependency) -> dict:
    repo = UserRepository(db)
    service = UserService(repo)
    
    return service.refresh(refresh_token=refresh_token.refresh)


@router.post("/logout/")
def logout(refresh_token: RefreshIn, db:db_dependency, access_token: jwt_dependency) -> dict:
    repo = UserRepository(db)
    service = UserService(repo)
    
    return service.logout(refresh_token.refresh)
    
@router.post("/me/", response_model=Me)
def me(db: db_dependency, access_token: jwt_dependency):
    repo = UserRepository(db)
    service = UserService(repo)
    
    return service.me(access_token=access_token)

@router.post("/update/", response_model=ProfilUpdateOut)
def update(db:db_dependency, access_token: jwt_dependency, user_in: ProfilUpdateIn):
    repo = UserRepository(db)
    service = UserService(repo)
    
    return service.update(access_token=access_token, user_in=user_in)
    
    