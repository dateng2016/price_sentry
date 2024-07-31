# from sqlalchemy.orm import Session
import random
from typing import Annotated, Union
from fastapi import Depends
import hashlib
import jwt
import datetime
from fastapi.responses import JSONResponse
import smtplib
from sqlalchemy.ext.asyncio import AsyncSession
from email.message import EmailMessage
import logging


from config import *
from lib.otp_storage import SessionStore
from lib import schemas
from db import crud, get_async_db


sessions = SessionStore()
SettingsDep = Annotated[Settings, Depends(get_settings)]
AsyncSessionDep = Annotated[AsyncSession, Depends(get_async_db)]


logger = logging.getLogger(name=__name__)
logger.setLevel(level=logging.INFO)
formatter = logging.Formatter(fmt="%(asctime)s - %(levelname)s - %(message)s")
file_handler = logging.FileHandler(filename="log/user.log", mode="a")
file_handler.setFormatter(fmt=formatter)
logger.addHandler(hdlr=file_handler)


class UserService:
    def __init__(self, settings: SettingsDep, async_db: AsyncSessionDep) -> None:
        self.email_from = settings.email_from
        self.app_password = settings.app_password
        self.secret = settings.secret
        self.async_db = async_db

    def sign_in(self, email: str) -> Union[schemas.SessionResp, schemas.FailureResp]:
        try:
            otp = self.get_random_otp()
            session_id = sessions.create_session(data={"otp": otp, "email": email})
            logger.info(
                f"User email {email} signing in. Session id: {session_id}. OTP code {otp}."
            )
            print(f"Session id: {session_id}. OTP code {otp} sent to {email}")
            # Uncomment during production
            # self.send_otp_via_email(email, otp)
            return schemas.SessionResp(session_id=session_id)
        except Exception as err:
            logger.error(f"Failed to send OTP code to {email}. {err}")
            return schemas.FailureResp(
                detail=f"Sign in failed. Failed to send OTP code to {email}. "
            )

    async def confirm(
        self, session_id: str, otp_code: str
    ) -> Union[schemas.TokenResp, schemas.FailureResp]:
        session = sessions.retrieve_session_data(session_id)
        if (
            session is None
            or session.get("data") is None
            or session.get("data").get("otp") is None
        ):
            return schemas.FailureResp(detail=str("Invalid session id"))
        expected_otp = session["data"]["otp"]
        if otp_code != expected_otp:
            return schemas.FailureResp(detail=str("Invalid OTP"))
        sessions.end_session(session_id=session_id)
        email = session["data"]["email"]
        user = await crud.get_user_by_email(db=self.async_db, email=email)
        if not user:
            print("Creating a new user")
            id = self.sha256(email=email)
            user = schemas.User(id=id, email=email)
            await crud.create_user(db=self.async_db, user=user)
            token = self.gen_jwt_token(user=user)
            return schemas.TokenResp(token=token, new=True)
        else:
            token = self.gen_jwt_token(user=user)
            return schemas.TokenResp(token=token, new=False)

    async def get_user_by_id(self, user_id: str) -> Optional[schemas.User]:
        return await crud.get_user_by_id(db=self.async_db, user_id=user_id)

    async def update_user(
        self, user_id: str, first_name: str, last_name: str
    ) -> Union[schemas.SuccessResp, schemas.FailureResp]:
        try:
            await crud.update_user(
                db=self.async_db,
                user_id=user_id,
                first_name=first_name,
                last_name=last_name,
            )
            return schemas.SuccessResp(detail="Successfully updated user info")
        except Exception as err:
            return schemas.FailureResp(
                detail="Unable to update user info at the moment, please try again later"
            )

    def get_random_otp(self) -> str:
        return str(random.randint(10000, 99999))

    def send_otp_via_email(self, email_to: str, otp: str):
        try:
            msg = EmailMessage()
            msg.set_content(
                f"Here is your One-Time-Password: {otp}. Please do not share this with anyone else."
            )

            msg["Subject"] = "Log In Code for Price Sentry"
            msg["From"] = self.email_from
            msg["To"] = email_to

            # Connect to Gmail's SMTP server
            connection = smtplib.SMTP("smtp.gmail.com", 587)
            connection.starttls()
            connection.login(user=self.email_from, password=self.app_password)
            connection.send_message(msg=msg)
            connection.quit()
        except Exception as err:
            print(err)

    def sha256(self, email: str):
        m = hashlib.sha256()
        m.update(bytes(email, "utf-8"))
        return m.hexdigest()

    def gen_jwt_token(self, user: schemas.User) -> str:
        payload = {
            "user_id": user.id,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(days=365),
        }
        return jwt.encode(payload=payload, key=self.secret, algorithm="HS256")
