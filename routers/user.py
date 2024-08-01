from fastapi import APIRouter
from fastapi import Depends
from typing import Annotated, Union
from fastapi.responses import JSONResponse

from services.user_service import UserService
from lib import schemas
from lib.utils import UserAuthDep

router = APIRouter(prefix="/user", tags=["User"])

# Dependency
UserServiceDep = Annotated[UserService, Depends(UserService)]


@router.post("/sign_in_otp")
def sign_in_otp(
    sign_in_req: schemas.SignInOtpReq, user_service: UserServiceDep
) -> Union[schemas.SessionResp, schemas.FailureResp]:
    """
    Endpoint for signing in a user via OTP.

    This endpoint generates a one-time password (OTP) for the specified email address,
    creates a session for the user, and returns the session ID.

    Args:
        sign_in_req (schemas.SignInOtpReq): Request schema containing the email address of the user.
        user_service (UserServiceDep): Dependency injection for the user service that handles OTP generation and session creation.

    Returns:
        Union[schemas.SuccessResp, schemas.FailureResp]:
            - `schemas.SuccessResp` with a success message if the sign in is successful.
            - `schemas.FailureResp` with an error detail if the sign in fails.

    """
    return user_service.sign_in(email=sign_in_req.email)


@router.post("/confirm_otp")
async def confirm_otp(
    confirm_otp_req: schemas.ConfirmOtpReq, user_service: UserService = Depends()
) -> Union[schemas.TokenResp, schemas.FailureResp]:
    """
    Verify the OTP code and authenticate the user based on the session data.

    This method retrieves session data using the provided session ID, validates the OTP code, and performs the
    following actions:
    - Ends the session if the OTP is valid.
    - Retrieves or creates a user associated with the email from the session data.
    - Generates and returns a JWT token for the authenticated user.

    Args:
        session_id (str): The ID of the session containing the OTP and user email.
        otp_code (str): The OTP code provided by the user to confirm their identity.

    Returns:
        Union[schemas.TokenResp, schemas.FailureResp]:
            - `schemas.TokenResp` with a JWT token and a flag indicating if the user is new or existing, if the OTP
              is valid and the authentication is successful.
            - `schemas.FailureResp` with an error detail if the OTP is invalid or the session ID is not valid.

    Notes:
        - Logs are generated for various steps, including session retrieval, OTP validation, and user creation.
        - The `session_id` is used to fetch the OTP and email from the session data.
        - If the OTP is incorrect or the session is invalid, a failure response is returned.
        - If the user is not found in the database, a new user is created.
        - The `gen_jwt_token` method is used to generate a JWT token for authenticated users.

    Raises:
        Exception: If any error occurs during session retrieval, OTP validation, user creation, or token generation.
    """
    return await user_service.confirm(
        session_id=confirm_otp_req.session_id, otp_code=confirm_otp_req.otp_code
    )


@router.get("/info")
async def get_user_info(
    user_id: UserAuthDep, user_service: UserService = Depends()
) -> schemas.User:
    """
    Retrieve user information based on the user ID.

    This endpoint fetches and returns user details for the specified user ID. The user ID is obtained from the
    authenticated user's context. It relies on the `UserService` to access user data.

    Args:
        user_id (UserAuthDep): The authenticated user ID extracted from the request context. This parameter is
            typically managed by a dependency that provides the authenticated user's ID.
        user_service (UserService, optional): Dependency injection for the user service that retrieves user data.
            Defaults to `Depends()`.

    Returns:
        schemas.User: A schema object containing the user details associated with the provided user ID.

    Raises:
        HTTPException: Raises a 404 Not Found error if the user ID does not correspond to any user in the database.

    Notes:
        - Ensure that the user ID provided is valid and corresponds to an existing user.
        - This endpoint requires authentication, and the user ID must be authorized to access this endpoint.
    """
    user = await user_service.get_user_by_id(user_id=user_id)
    return user


@router.post("/info")
async def update_user_info(
    user_info_req: schemas.UserUpdateReq,
    user_id: UserAuthDep,
    user_service: UserService = Depends(),
) -> Union[schemas.SuccessResp, schemas.FailureResp]:
    """
    Update user information for the authenticated user.

    This endpoint updates the first name and last name of the user with the specified user ID. The user ID is
    obtained from the authenticated user's context. It relies on the `UserService` to perform the update operation.

    Args:
        user_info_req (schemas.UserUpdateReq): Request schema containing the updated first name and last name.
        user_id (UserAuthDep): The authenticated user's ID. This parameter is typically managed by a dependency
            that provides the authenticated user's ID.
        user_service (UserService, optional): Dependency injection for the user service that handles user updates.
            Defaults to `Depends()`.

    Returns:
        Union[schemas.SuccessResp, schemas.FailureResp]:
            - `schemas.SuccessResp` with a success message if the user information is updated successfully.
            - `schemas.FailureResp` with an error detail if the update fails.

    Raises:
        HTTPException: Raises an HTTP 400 Bad Request error if the provided data is invalid.

    Notes:
        - Ensure that the authenticated user has permission to update the provided user ID.
        - Validations on the `user_info_req` data should be performed to ensure correct and complete data.
    """
    return await user_service.update_user(
        user_id=user_id,
        first_name=user_info_req.first_name,
        last_name=user_info_req.last_name,
    )


@router.delete("/info")
async def delete_user(
    user_id: UserAuthDep, user_service: UserServiceDep
) -> Union[schemas.SuccessResp, schemas.FailureResp]:
    """
    Delete a user from the system.

    This endpoint deletes the user associated with the provided user ID. The user ID is extracted from the
    authenticated user's context. The `UserService` is used to perform the deletion operation.

    Args:
        user_id (UserAuthDep): The authenticated user's ID, which is managed by a dependency that provides
            the authenticated user's ID.
        user_service (UserServiceDep): Dependency injection for the user service that handles user deletion.

    Returns:
        Union[schemas.SuccessResp, schemas.FailureResp]:
            - `schemas.SuccessResp` with a success message if the user is deleted successfully.
            - `schemas.FailureResp` with an error detail if the deletion fails.

    Raises:
        HTTPException: Raises an HTTP 400 Bad Request error if the user ID is invalid or if the deletion fails.

    Notes:
        - Ensure that the authenticated user has permission to delete the specified user.
        - This endpoint may require additional checks to confirm the user's identity and authorization.
    """
    return await user_service.delete_user(user_id=user_id)
