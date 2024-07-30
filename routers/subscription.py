from fastapi import APIRouter, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends
from typing import Annotated, Union, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import JSONResponse


from services.user_service import UserService
from services.subscription_service import SubscriptionService
from lib import schemas
from config import Settings, get_settings
from lib.utils import UserAuthDep
from scraper.amazon import amazon_search
from db import crud
from db.base import get_async_db

router = APIRouter(prefix="/sub", tags=["Subscription"])

# Dependency
SubServiceDep = Annotated[UserService, Depends(SubscriptionService)]
AsyncSessionDep = Annotated[AsyncSession, Depends(get_async_db)]


@router.get("/search")
def search(
    user_id: UserAuthDep, kw: str, vendor: schemas.VendorType, include: str = None
) -> Optional[List[schemas.Product]]:

    if vendor == "amazon":
        products = amazon_search.amazon_search(keyword=kw, include=include)
        return products


@router.post("/subscribe")
async def subscribe(
    user_id: UserAuthDep, product: schemas.Product, db: AsyncSessionDep
):
    link_id = product.link_id
    # First look through the subscription table to see if the combination already existed
    subscription = await crud.get_subscription(db=db, user_id=user_id, link_id=link_id)

    # The subscription already exists
    if subscription:
        # print(res.user_id, res.link_id)
        return schemas.SubFailure(detail="You have already subscribed to this product")

    # Now we create a new subscription
    await crud.create_subscription(db=db, user_id=user_id, link_id=link_id)

    # Check if the product already exists in the Product table
    product_in_db = await crud.get_product_by_id(db=db, link_id=link_id)

    # It already exists. Do nothing
    if product_in_db:
        return

    await crud.create_product(db=db, product=product)
    return schemas.SubSuccess()


@router.get("/prod")
def get_product(
    user_id: UserAuthDep, sub_service: SubServiceDep
) -> Optional[List[schemas.Product]]:
    pass
