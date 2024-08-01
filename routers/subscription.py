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
    """
    Search for products based on specified criteria.

    This endpoint allows users to search for products from a specific vendor using a keyword. It uses the
    `SubService` to perform the search operation and returns a list of products that match the search criteria.

    Args:
        user_id (UserAuthDep): The authenticated user's ID, provided by a dependency that manages user
            authentication.
        sub_service (SubServiceDep): Dependency injection for the service that performs the product search.
        kw (str): The search keyword to find products.
        vendor (schemas.VendorType): The vendor to search for products from. This should be a valid vendor type
            defined in the `VendorType` schema.
        include (str, optional): A keyword that must be included in the product's description. Default is `None`.
        max_prod (int, optional): The maximum number of products to return. Default is 3.

    Returns:
        Optional[List[schemas.Product]]:
            - A list of `schemas.Product` objects if products are found that match the search criteria.
            - `None` if no products are found.

    Raises:
        HTTPException: Raises an HTTP 400 Bad Request error if any of the provided parameters are invalid.

    Notes:
        - Ensure that the `vendor` is a supported value and properly mapped in the `VendorType` schema.
        - The search functionality may be vendor-specific, so the behavior might differ based on the selected vendor.
        - If the `include` parameter is provided, only products containing that keyword will be considered in the results.
    """
    return sub_service.search(
        user_id=user_id, kw=kw, vendor=vendor, include=include, max_prod=max_prod
    )


# Get all the products that the user subscribes to
@router.get("/products")
async def get_products(user_id: UserAuthDep, sub_service: SubServiceDep):
    """
    Retrieve a list of products associated with the authenticated user.

    This endpoint retrieves all products that the authenticated user is subscribed to. It uses the `SubService`
    to fetch the list of products based on the user's subscriptions.

    Args:
        user_id (UserAuthDep): The authenticated user's ID, provided by a dependency that manages user
            authentication.
        sub_service (SubServiceDep): Dependency injection for the service that retrieves the user's products.

    Returns:
        List[schemas.Product]:
            - A list of `schemas.Product` objects representing the products associated with the user's subscriptions.

    Raises:
        HTTPException: Raises an HTTP 404 Not Found error if no products are found for the user.

    Notes:
        - Ensure that the user is authenticated and authorized to access the product data.
        - This endpoint assumes that the `user_id` corresponds to an existing user with associated subscriptions.
    """
    return await sub_service.get_products(user_id=user_id)


@router.post("/product")
async def subscribe(
    user_id: UserAuthDep, product: schemas.Product, sub_service: SubServiceDep
) -> Union[schemas.SuccessResp, schemas.FailureResp]:
    """
    Subscribe the authenticated user to a product.

    This endpoint allows a user to subscribe to a product by specifying the product's details. It checks if
    the user is already subscribed to the product and creates a new subscription if not. Additionally, it
    ensures that the product exists in the database or creates a new product entry if necessary.

    Args:
        user_id (UserAuthDep): The ID of the authenticated user making the subscription request.
        product (schemas.Product): The product details that the user wants to subscribe to.
        sub_service (SubServiceDep): Dependency injection for the service handling subscription logic.

    Returns:
        Union[schemas.SuccessResp, schemas.FailureResp]:
            - `schemas.SuccessResp`: Indicates a successful subscription with a message.
            - `schemas.FailureResp`: Indicates failure to subscribe, with a detailed error message.

    Raises:
        HTTPException: May raise an HTTP 400 Bad Request if there are issues with the subscription request.

    Notes:
        - The method first checks if the subscription already exists. If it does, it returns a failure response.
        - If the subscription does not exist, it creates a new subscription and checks if the product exists in
          the database. If not, it creates a new product entry.
        - The product's details should include a valid `link_id` for subscription management.
    """
    return await sub_service.subscribe(user_id=user_id, product=product)


@router.delete("/product/{link_id}")
async def unsubscribe(
    user_id: UserAuthDep, link_id: str, sub_service: SubServiceDep
) -> Union[schemas.SuccessResp, schemas.FailureResp]:
    return await sub_service.unsubscribe(user_id=user_id, link_id=link_id)
