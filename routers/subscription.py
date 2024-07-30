from fastapi import APIRouter, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends
from typing import Annotated, Union, Optional, List
from fastapi.responses import JSONResponse


from services.user_service import UserService
from services.subscription_service import SubscriptionService
from lib import schemas
from config import Settings, get_settings
from lib.utils import UserAuthDep
from scraper.amazon import amazon_search

router = APIRouter(prefix="/sub", tags=["Subscription"])

# Dependency
SubServiceDep = Annotated[UserService, Depends(SubscriptionService)]


@router.get("/search")
def search(
    user_id: UserAuthDep, kw: str, vendor: str
) -> Optional[List[schemas.Product]]:
    amazon_search.amazon_search(
        keyword=kw,
    )


@router.get("/prod")
def get_product(
    user_id: UserAuthDep, sub_service: SubServiceDep
) -> Optional[List[schemas.Product]]:
    pass
