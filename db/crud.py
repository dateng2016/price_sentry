# from sqlalchemy.orm import Session
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
import logging

from lib import schemas
from db import models


logger = logging.getLogger(name=__name__)
logger.setLevel(level=logging.INFO)
formatter = logging.Formatter(fmt="%(asctime)s - %(levelname)s - %(message)s")
file_handler = logging.FileHandler(filename="log/db.log", mode="a")
file_handler.setFormatter(fmt=formatter)
logger.addHandler(hdlr=file_handler)


async def get_user_by_id(db: AsyncSession, user_id: str) -> Optional[schemas.User]:
    try:
        logger.info(f"Getting user by id: {user_id}")
        res = await db.execute(select(models.User).where(models.User.id == user_id))
        user = res.scalar()
        print(f"Found user: {user}")
        return user
    except Exception as err:
        logger.error(f"Failed to get user by id: {user_id}. {err}")
        return None


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[schemas.User]:
    try:
        logger.info(f"Getting user by email: {email}")
        res = await db.execute(select(models.User).where(models.User.email == email))
        user = res.scalar()
        return user
    except Exception as err:
        logger.error(f"Failed to get user by email: {email}. {err}")
        return None


async def create_user(db: AsyncSession, user: schemas.User):
    try:
        logger.info(f"Creating user with email: {user.email}")
        user = models.User(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
        )
        db.add(user)
        await db.commit()
    except Exception as err:
        logger.error(f"Failed to create user with email: {user.email}. {err}")
        return


async def update_user(db: AsyncSession, user_id: str, first_name: str, last_name: str):
    try:
        logger.info(f"Updating user info with user_id {user_id}")
        await db.execute(
            update(models.User)
            .where(models.User.id == user_id)
            .values(first_name=first_name, last_name=last_name)
        )
        await db.commit()
    except Exception as err:
        logger.error(f"Failed to update user info with user_id {user_id}. {err}")
        return


async def get_product_by_id(
    db: AsyncSession, link_id: str
) -> Optional[List[schemas.Product]]:
    try:
        logger.info(f"Getting product by link id: {link_id}")
        res = await db.execute(
            select(models.Product).where(models.Product.link_id == link_id)
        )
        product = res.scalar()
        return product
    except Exception as err:
        logger.error(f"Failed to get product by link id: {link_id}. {err}")
        return


async def create_product(db: AsyncSession, product: schemas.Product):
    try:
        logger.info(
            f"Creating product with title {product.title}, vendor of {schemas.Vendor(product.vendor)}, link {product.link}, link id {product.link_id}, img src {product.img_src}, price {product.price}"
        )
        product_to_create = models.Product(
            title=product.title,
            vendor=product.vendor,
            link=product.link,
            link_id=product.link_id,
            img_src=product.img_src,
            price=product.price,
        )
        db.add(product_to_create)
        await db.commit()
    except Exception as err:
        logger.error(
            f"Failed to create product with title {product.title}, vendor of {schemas.Vendor(product.vendor)}, link {product.link}, link id {product.link_id}, img src {product.img_src}, price {product.price}. {err}"
        )


async def get_subscription(
    db: AsyncSession, user_id: str, link_id: str
) -> Optional[schemas.Subscription]:
    try:
        logger.info(f"Getting subscription by user id {user_id} and link id {link_id}")
        res = await db.execute(
            select(models.Subscription).where(
                models.Subscription.user_id == user_id,
                models.Subscription.link_id == link_id,
            )
        )
        subscription = res.scalar()
        return subscription
    except Exception as err:
        logger.error(
            f"Failed to get subscription by user id {user_id} and link id {link_id}. {err}"
        )


async def create_subscription(db: AsyncSession, user_id: str, link_id: str):
    try:
        logger.info(f"Creating subscription by user id {user_id} and link id {link_id}")
        subscription = models.Subscription(user_id=user_id, link_id=link_id)
        db.add(subscription)
        await db.commit()
        return "Success"
    except Exception as err:
        logger.error(
            f"Failed ti create subscription by user id {user_id} and link id {link_id}. {err}"
        )


async def get_all_sub(db: AsyncSession, user_id: str):
    try:
        logger.info(f"Getting all subscriptions for user with user id {user_id}")
        res = await db.execute(
            select(models.Subscription).where(models.Subscription.user_id == user_id)
        )
        subscriptions = res.scalars().all()
        return subscriptions
    except Exception as err:
        logger.error(
            f"Failed to get all subscriptions for user with user id {user_id}. {err}"
        )


async def unsubscribe(db: AsyncSession, user_id: str, link_id: str):
    try:
        logger.info(
            f"Unsubscribing product with link id {link_id} for user with user id {user_id}"
        )
        # First we remove the subscription related to this user_id & link_id
        res = await db.execute(
            select(models.Subscription).where(
                models.Subscription.user_id == user_id,
                models.Subscription.link_id == link_id,
            )
        )
        subscription = res.scalar()
        await db.delete(subscription)
        await db.commit()
        # Now we check in the subscription table if there is another row with the same link_id

        res = await db.execute(
            select(models.Subscription).where(models.Subscription.link_id == link_id)
        )
        subscription = res.scalar()
        # If there is another subscription in there, we do nothing,
        if subscription:
            return

        # If not, we get rid of the product in the product table
        logger.info(
            f"No more users subscribe to the product with link id {link_id}, removing this product from the product table"
        )
        res = await db.execute(
            select(models.Product).where(models.Product.link_id == link_id)
        )
        product = res.scalar()
        await db.delete(product)
        await db.commit()

    except Exception as err:
        logger.error(
            f"Failed to unsubscribe product with link id {link_id} for user with user id {user_id}. {err}"
        )
