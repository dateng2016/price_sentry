from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Dict
import decimal


class FailureResp(BaseModel):
    detail: str
    status: str = "failure"


class SignInOtpReq(BaseModel):
    email: str


class ConfirmOtpReq(BaseModel):
    session_id: str
    otp_code: str


class User(BaseModel):
    id: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None

    class Config:
        from_attributes = True


class UserUpdateReq(BaseModel):
    first_name: str
    last_name: str


class TokenResp(BaseModel):
    token: str
    new: bool


class Product(BaseModel):
    title: str
    link_href: str
    img_src: str
    link_id: str
    price: float


class SuccessResp(BaseModel):
    status: str = "success"


class FailureResp(BaseModel):
    detail: str
    status: str = "failure"
