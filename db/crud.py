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


async def get_product_by_id(
    db: AsyncSession, link_id: str
) -> Optional[List[schemas.Product]]:
    try:
        res = await db.execute(
            select(models.Product).where(models.Product.link_id == link_id)
        )
        product = res.scalar()
        print(product)
        return product
    except Exception as err:
        print(err)


async def get_subscription(
    db: AsyncSession, user_id: str, link_id: str
) -> Optional[schemas.Subscription]:
    try:
        res = await db.execute(
            select(models.Subscription).where(
                models.Subscription.user_id == user_id,
                models.Subscription.link_id == link_id,
            )
        )
        subscription = res.scalar()

        return subscription
    except Exception as err:
        print(err)


async def create_subscription(db: AsyncSession, user_id: str, link_id: str):
    try:
        subscription = models.Subscription(user_id=user_id, link_id=link_id)
        db.add(subscription)
        await db.commit()
        return "Success"
    except Exception as err:
        print(err)
