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

from config import *
from lib.otp_storage import SessionStore
from lib import schemas
from db import crud, get_async_db


SettingsDep = Annotated[Settings, Depends(get_settings)]
AsyncSessionDep = Annotated[AsyncSession, Depends(get_async_db)]


class SubscriptionService:
    def __init__(self, settings: SettingsDep, async_db: AsyncSessionDep) -> None:
        self.email_from = settings.email_from
        self.app_password = settings.app_password
        self.secret = settings.secret
        self.async_db = async_db

    # def search()
