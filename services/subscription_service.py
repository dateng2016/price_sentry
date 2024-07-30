import random
from typing import Annotated, Union
from fastapi import Depends
import hashlib
import jwt
import datetime
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
import smtplib
from sqlalchemy.ext.asyncio import AsyncSession
from email.message import EmailMessage
from lib.otp_storage import SessionStore
from lib import schemas
from db import crud, get_async_db
from scraper.amazon.amazon_search import *
from enum import Enum

from config import *


SettingsDep = Annotated[Settings, Depends(get_settings)]
AsyncSessionDep = Annotated[AsyncSession, Depends(get_async_db)]


class SubscriptionService:
    def __init__(self, settings: SettingsDep, async_db: AsyncSessionDep) -> None:
        self.email_from = settings.email_from
        self.app_password = settings.app_password
        self.secret = settings.secret
        self.async_db = async_db

    def get_product(self, user_id: str) -> Optional[List[schemas.Product]]:
        pass

    def search(self, link: str) -> Optional[schemas.Product]:
        pass

    async def subscribe(self, user_id: str, link: str):
        # First check if the link already exists in the Product table
        # If exists, we don't worry about it, if not, we create another
        # row in the product table
        pass

    def sha256(self, link: str):
        m = hashlib.sha256()
        m.update(bytes(link, "utf-8"))
        return m.hexdigest()
