from fastapi import APIRouter, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends
from typing import Annotated, Union
from fastapi.responses import JSONResponse
from ..services.user_service import UserService
from ..lib import schemas
from app.config import Settings, get_settings
from app.lib.utils import UserAuthDep

router = APIRouter(prefix="/user", tags=["User"])

# Dependency
UserServiceDep = Annotated[UserService, Depends(UserService)]
SettingsDep = Annotated[Settings, Depends(get_settings)]


@router.post("/sign_in_otp")
def sign_in_otp(
    sign_in_req: schemas.SignInOtpReq, user_service: UserServiceDep
) -> JSONResponse:
    return user_service.sign_in(sign_in_req.email)


@router.post("/confirm_otp")
async def confirm_otp(
    confirm_otp_req: schemas.ConfirmOtpReq, user_service: UserService = Depends()
) -> Union[schemas.TokenResp, schemas.FailureResp]:
    return await user_service.confirm(
        confirm_otp_req.session_id, confirm_otp_req.otp_code
    )


@router.get("/info")
async def get_user_info(
    user_id: UserAuthDep, user_service: UserService = Depends()
) -> schemas.User:
    # Update user info
    print(f" Here is the user id from jwt token: {user_id}")
    user = await user_service.get_user_by_id(user_id=user_id)
    return user


@router.post("/info")
async def update_user_info(
    user_info_req: schemas.UserUpdateReq,
    user_id: UserAuthDep,
    user_service: UserService = Depends(),
) -> schemas.SuccessResp:
    await user_service.update_user(
        user_id=user_id,
        first_name=user_info_req.first_name,
        last_name=user_info_req.last_name,
    )
    return schemas.SuccessResp()
