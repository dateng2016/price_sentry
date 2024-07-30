from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Dict, Literal
import decimal
from enum import Enum

VendorType = Literal["amazon", "bestbuy", "ebay"]


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
    vendor: int
    link: str
    link_id: str
    img_src: str
    price: float


class SuccessResp(BaseModel):
    status: str = "success"


class FailureResp(BaseModel):
    detail: str
    status: str = "failure"


# class SubReq(BaseModel):
#     email: str
#     link: str


class Vendor(Enum):
    AMAZON = 1
    BESTBUY = 2
    EBAY = 3
    TARGET = 4
