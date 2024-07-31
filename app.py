from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from typing_extensions import Annotated

from routers import *
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

    return "Price Sentry is up and running."


from sqlalchemy.ext.asyncio import AsyncSession

AsyncSessionDep = Annotated[AsyncSession, Depends(get_async_db)]


# this api is used for various testing for different apis
@app.get("/testing")
async def testing(request: Request, user_id: UserAuthDep, db: AsyncSessionDep):
    x = await crud.unsubscribe(
        db=db,
        user_id=user_id,
        link_id="1986d4da1676bf025a201c648b3319dd30ea7fb68fb327fa0e35f4d9a2b938db",
    )

    return x
