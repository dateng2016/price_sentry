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

from app.routers.user import router as user_router
from app.config import get_settings
from app.db import models, crud, get_sync_db, get_async_db, sync_engine
from app.lib.utils import UserAuthDep

load_dotenv()


def start_app():
    app = FastAPI(swagger_ui_parameters={"syntaxHighlight": False})
    app.include_router(router=user_router)
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
