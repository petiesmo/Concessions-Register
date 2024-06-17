#TODO: Get this working later - extracted from main fastapi app
from fastapi import FastAPI, Depends, HTTPException, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
#from fastapi_users import FastAPIUsers
#from fastapi_users.authentication import JWTAuthentication
#from fastapi_users.db import SQLAlchemyUserDatabase

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import Session, select
from db.models import BaseSQLModel, User

async def get_user_db(session: AsyncSession = Depends(get_session)):
    yield SQLAlchemyUserDatabase(session, User)
jwt_authentication = JWTAuthentication(secret=SECRET, lifetime_seconds=3600)

fastapi_users = FastAPIUsers(
    get_user_db,
    [jwt_authentication],
)

app.include_router(
    fastapi_users.get_auth_router(jwt_authentication), prefix="/auth/jwt", tags=["auth"]
)

app.include_router(
    fastapi_users.get_register_router(), prefix="/auth", tags=["auth"]
)

app.include_router(
    fastapi_users.get_users_router(), prefix="/users", tags=["users"]
)