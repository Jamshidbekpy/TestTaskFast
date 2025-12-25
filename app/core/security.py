from jwt import decode

from app.core.settings import settings


SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM

def get_user_id_from_jwt(token: str) -> int:
    payload = decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    return payload["sub"]