from fastapi import APIRouter
from fastapi import Depends
from typing import Annotated, Union, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession


from services.user_service import UserService
from services.subscription_service import SubscriptionService
from lib import schemas
from lib.utils import UserAuthDep
from scraper.amazon import amazon_search
from db import crud
from db.base import get_async_db

router = APIRouter(prefix="/sub", tags=["Subscription"])

# Dependency
SubServiceDep = Annotated[SubscriptionService, Depends(SubscriptionService)]
AsyncSessionDep = Annotated[AsyncSession, Depends(get_async_db)]


@router.get("/search")
def search(
    user_id: UserAuthDep,
    sub_service: SubServiceDep,
    kw: str,
    vendor: schemas.VendorType,
    include: str = None,
) -> Optional[List[schemas.Product]]:
    return sub_service.search(
        user_id=user_id,
        kw=kw,
        vendor=vendor,
        include=include,
    )


# Get all the products that the user subscribes to
@router.get("/products")
async def get_products(user_id: UserAuthDep, sub_service: SubServiceDep):
    return await sub_service.get_products(user_id=user_id)


@router.post("/product")
async def subscribe(
    user_id: UserAuthDep, product: schemas.Product, sub_service: SubServiceDep
) -> Union[schemas.SuccessResp, schemas.FailureResp]:
    return await sub_service.subscribe(user_id=user_id, product=product)


@router.delete("/product/{link_id}")
async def unsubscribe(db: AsyncSessionDep, user_id: UserAuthDep, link_id: str):
    # First delete the subscription with this user_id and link_id
    pass
