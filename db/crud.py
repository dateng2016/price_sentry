from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from lib import schemas
from db import models


async def get_user_by_id(db: AsyncSession, user_id: str) -> Optional[schemas.User]:
    try:
        res = await db.execute(select(models.User).where(models.User.id == user_id))
        user = res.scalar()
        print(f"Found user: {user}")
        return user
    except Exception as err:
        print(f"Error occured: {err}")
        return None


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[schemas.User]:
    try:
        res = await db.execute(select(models.User).where(models.User.email == email))
        user = res.scalar()
        return user
    except Exception as err:
        print(err)
        return None


async def create_user(db: AsyncSession, user: schemas.User):
    try:
        user = models.User(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
        )
        db.add(user)
        await db.commit()
    except Exception as err:
        print(err)


async def update_user(db: AsyncSession, user_id: str, first_name: str, last_name: str):
    try:
        await db.execute(
            update(models.User)
            .where(models.User.id == user_id)
            .values(first_name=first_name, last_name=last_name)
        )
        await db.commit()
    except Exception as err:
        print(err)


async def get_product_by_user_id(
    db: AsyncSession, user_id: str
) -> Optional[List[schemas.Product]]:
    pass
