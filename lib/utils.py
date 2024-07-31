import jwt
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Annotated, Union
import logging
import hashlib

from config import *

security = HTTPBearer()
SettingsDep = Annotated[Settings, Depends(get_settings)]


def parse_jwt_token(token: str, secret: str):
    try:
        # in case token is "Bearer token"
        if " " in token:
            token = token.split(" ")[1]
        return jwt.decode(jwt=token, key=secret, algorithms=["HS256"])
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
    payload = parse_jwt_token(token=token.credentials, secret=settings.secret)
    if payload and payload.get("user_id"):
        return payload.get("user_id")
    raise HTTPException(status_code=401, detail="Missing authentication credentials")


UserAuthDep = Annotated[str, Depends(get_user_id)]


def hash256(keyword: str) -> str:
    """
    Generate SHA-256 hash of a given string.

    :param keyword: The string to be hashed.
    :return: The SHA-256 hash of the string in hexadecimal format.
    """
    # Create a new SHA-256 hash object
    sha256 = hashlib.sha256()

    # Update the hash object with the bytes of the string
    sha256.update(keyword.encode("utf-8"))

    # Return the hexadecimal representation of the hash
    return sha256.hexdigest()


def get_logger(
    name: str,
    filename: str,
    filemode: str = "a",
    level=logging.INFO,
    fmt="%(asctime)s - %(levelname)s - %(message)s",
) -> logging.Logger:
    logger = logging.getLogger(name=name)
    logger.setLevel(level=level)
    formatter = logging.Formatter(fmt=fmt)
    file_handler = logging.FileHandler(filename=filename, mode=filemode)
    file_handler.setFormatter(fmt=formatter)
    logger.addHandler(hdlr=file_handler)
    return logger
