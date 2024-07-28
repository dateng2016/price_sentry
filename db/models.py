from .base import Base
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.types import DECIMAL
from sqlalchemy.orm import relationship
from .base import Base


class User(Base):
    __tablename__ = "user"

    id = Column(String(64), primary_key=True)
    email = Column(String(64), unique=True, index=True)
    first_name = Column(String(30))
    last_name = Column(String(30))
