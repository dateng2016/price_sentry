from fastapi import FastAPI, Depends, Request, HTTPException
from pydantic import BaseModel
import logging
import logging.handlers
from contextlib import contextmanager
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from fastapi.staticfiles import StaticFiles
from fastapi import APIRouter
import os
from typing_extensions import Annotated

from fastapi import FastAPI, Depends, Request, HTTPException, Header
from pydantic import BaseModel
from typing_extensions import Annotated
from sqlalchemy.orm import Session
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Union, Optional, List
import logging
import logging.handlers
from contextlib import contextmanager
from fastapi import APIRouter
from enum import Enum

from routers import *
from config import get_settings
from db import models, crud, get_sync_db, get_async_db, sync_engine
from lib.utils import UserAuthDep

load_dotenv()


def start_app():
    app = FastAPI(swagger_ui_parameters={"syntaxHighlight": False})
    app.include_router(router=user_router)
    app.include_router(router=sub_router)
    # settings = get_settings()

    origins = ["*"]  # Replace "*" with specific origins if needed
    app.add_middleware(
        CORSMiddleware, allow_origins=origins, allow_methods=["*"], allow_headers=["*"]
    )
    models.Base.metadata.create_all(bind=sync_engine)
    return app


app = start_app()


@app.get("/health")
async def health(request: Request, user_id: UserAuthDep) -> str:

    return f"Price Sentry is up and running."


from sqlalchemy.ext.asyncio import AsyncSession

AsyncSessionDep = Annotated[AsyncSession, Depends(get_async_db)]


@app.get("/testing")
async def testing(request: Request, user_id: UserAuthDep, db: AsyncSessionDep):
    x = await crud.get_subscription(db=db, user_id=user_id, link_id="123")
    print(user_id)
    return x


# 2f0cadd212d820563995c4385e16a7b1f2453354bdaa31dd02889923608623f2
# 2f0cadd212d820563995c4385e16a7b1f2453354bdaa31dd02889923608623f2
