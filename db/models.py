from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.types import DECIMAL, SmallInteger
from sqlalchemy.orm import relationship
from .base import Base


class User(Base):
    __tablename__ = "user"

    id = Column(String(64), primary_key=True)
    email = Column(String(64), unique=True, index=True)
    first_name = Column(String(30))
    last_name = Column(String(30))


class Product(Base):
    __tablename__ = "product"

    title = Column(String(1024))
    vendor = Column(SmallInteger())
    link = Column(String(2048))
    link_id = Column(String(64), primary_key=True)
    img_src = Column(String(2048))
    price = Column(DECIMAL(precision=10, scale=2))


class Subscriptoin(Base):
    __tablename__ = "subscription"

    user_id = Column(String(64), primary_key=True)
    product_id = Column(String(64), primary_key=True)
