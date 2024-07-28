import jwt
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Annotated, Union
import os

from app.config import *

security = HTTPBearer()
SettingsDep = Annotated[Settings, Depends(get_settings)]


def parse_jwt_token(token: str, secret: str):
    try:
        # in case token is "Bearer token"
        if " " in token:
            token = token.split(" ")[1]
        return jwt.decode(token, secret, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        print("expired token")
        return None
    except jwt.InvalidTokenError:
        print("invalid token")
        return None


def get_user_id(
    token: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    settings: SettingsDep,
) -> Union[HTTPException, str]:
    payload = parse_jwt_token(token.credentials, settings.secret)
    if payload and payload.get("user_id"):
        return payload.get("user_id")
    raise HTTPException(status_code=401, detail="Missing authentication credentials")


UserAuthDep = Annotated[str, Depends(get_user_id)]
