from fastapi import APIRouter
from fastapi import Depends
from typing import Annotated, Union, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession


from services.subscription_service import SubscriptionService
from lib import schemas
from lib.utils import UserAuthDep
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
    max_prod: int = 3,
) -> Optional[List[schemas.Product]]:
    return sub_service.search(
        user_id=user_id, kw=kw, vendor=vendor, include=include, max_prod=max_prod
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
async def unsubscribe(
    user_id: UserAuthDep, link_id: str, sub_service: SubServiceDep
) -> Union[schemas.SuccessResp, schemas.FailureResp]:
    return await sub_service.unsubscribe(user_id=user_id, link_id=link_id)
