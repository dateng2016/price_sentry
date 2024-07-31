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
from scraper.amazon.amazon_search import amazon_search
from lib.utils import get_logger


SettingsDep = Annotated[Settings, Depends(get_settings)]
AsyncSessionDep = Annotated[AsyncSession, Depends(get_async_db)]

logger = get_logger(name=__name__, filename="log/subscription.log")


class SubscriptionService:
    def __init__(self, settings: SettingsDep, async_db: AsyncSessionDep) -> None:
        self.email_from = settings.email_from
        self.app_password = settings.app_password
        self.secret = settings.secret
        self.async_db = async_db

    def search(
        self, user_id: str, kw: str, vendor: schemas.VendorType, include: str = None
    ) -> Optional[List[schemas.Product]]:
        logger.info(
            f"Initializing product search for user id {user_id}, keyword {kw}, vendor {vendor}, must include keyword {include}"
        )
        if vendor == "amazon":
            products = amazon_search(keyword=kw, include=include)
            if products:
                logger.info(
                    f"Products found for user id {user_id}, keyword {kw}, vendor {vendor}, must include keyword {include}"
                )
                return products
            logger.info(
                f"Products not found for user id {user_id}, keyword {kw}, vendor {vendor}, must include keyword {include}"
            )

    async def get_products(self, user_id: str) -> Optional[List[schemas.Product]]:
        subscriptions = await crud.get_all_sub(db=self.async_db, user_id=user_id)
        products = []
        for sub in subscriptions:
            product = await crud.get_product_by_id(
                db=self.async_db, link_id=sub.link_id
            )
            products.append(product)
        return products

    async def subscribe(
        self, user_id: str, product: schemas.Product
    ) -> Union[schemas.SuccessResp, schemas.FailureResp]:
        logger.info(
            f"User with id {user_id} trying to subscribe to link {product.link}"
        )
        link_id = product.link_id
        # First look through the subscription table to see if the combination already existed
        subscription = await crud.get_subscription(
            db=self.async_db, user_id=user_id, link_id=link_id
        )

        # The subscription already exists
        if subscription:
            logger.info(
                f"The subscription with user id {user_id} and link id {link_id} already exists"
            )
            # print(res.user_id, res.link_id)
            return schemas.FailureResp(
                detail="You have already subscribed to this product"
            )

        # Now we create a new subscription
        await crud.create_subscription(
            db=self.async_db, user_id=user_id, link_id=link_id
        )

        # Check if the product already exists in the Product table
        product_in_db = await crud.get_product_by_id(db=self.async_db, link_id=link_id)

        # It already exists. Do nothing. If not create a new product
        if not product_in_db:
            logger.info(
                f"Creating a new product with link id {product.link_id} for user with id {user_id}"
            )
            await crud.create_product(db=self.async_db, product=product)
        return schemas.SuccessResp(
            detail="You have successfully subscribed to this product"
        )

    async def unsubscribe(
        self, user_id: str, link_id: str
    ) -> Union[schemas.SuccessResp, schemas.FailureResp]:
        logger.info(f"Unsubscribing for user {user_id} the product with id {link_id}")
        result = await crud.unsubscribe(
            db=self.async_db, user_id=user_id, link_id=link_id
        )
        return result
