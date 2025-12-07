from fastapi import FastAPI, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_session, AsyncSession
from starlette.responses import JSONResponse

from auth.jwt_utils import hash_password
from postgres.database import engine, get_session, async_sessionmaker
from postgres.models import RoleModel, StatusModel, UserModel

from routers.users_router import router as users_router
from routers.events_router import router as events_router
from routers.skills_router import router as skills_router
from routers.auth_router import router as auth_router
from routers.interests_router import router as interests_router
from routers.statuses_router import router as statuses_router

from schemas import Base

from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

app.include_router(users_router)
app.include_router(events_router)
app.include_router(skills_router)
app.include_router(auth_router)
app.include_router(interests_router)
app.include_router(statuses_router)

@app.on_event("startup")
async def setup_database_on_start():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    print("Database created successfully!")

    await initialize_roles()
    await initialize_statuses()
    await initialize_users()

async def initialize_roles():
    async with AsyncSession(engine, expire_on_commit=False) as session:
        roles_to_create = [
            RoleModel(name="ADMIN"),
            RoleModel(name="DEFAULT")
        ]

        session.add_all(roles_to_create)
        await session.commit()

async def initialize_statuses():
    async with AsyncSession(engine, expire_on_commit=False) as session:
        statuses_to_create = [
            StatusModel(name="Хочу сотрудничать"),
            StatusModel(name="Ищу людей в проект"),
            StatusModel(name="Ищу общение"),
        ]

        session.add_all(statuses_to_create)
        await session.commit()

async def initialize_users():
    async with AsyncSession(engine, expire_on_commit=False) as session:
        roles = (await session.execute(select(RoleModel).where(RoleModel.name.in_(["DEFAULT", "ADMIN"])))).scalars().all()

        users_to_create = [
            UserModel(
                username="ahmed",
                password=hash_password("ahmed"),
                bio="ahmed",
                first_name="ahmed",
                last_name="ahmed",
                roles=roles,
                status_id=2
            )
        ]

        session.add_all(users_to_create)
        await session.commit()

# ALLOWED_ORIGINS = [
#     "https://login.microsoftonline.com",
#     "https://example.com",
#     "http://localhost:3000",
# ]

# @app.middleware("http")
# async def cors_middleware(request: Request, call_next):
#     origin = request.headers.get("origin")
#
#     if not request.url.path.startswith("/api/auth"):
#         response = await call_next(request)
#         return response
#
#     if origin and origin not in ALLOWED_ORIGINS:
#         return JSONResponse(
#             status_code=403,
#             content={"error": "Origin not allowed"},
#             headers={"Access-Control-Allow-Origin": "null"}
#         )
#
#     response = await call_next(request)
#
#     if origin and origin in ALLOWED_ORIGINS:
#         response.headers["Access-Control-Allow-Origin"] = origin
#         response.headers["Access-Control-Allow-Credentials"] = "true"
#
#     return response