from fastapi import APIRouter, Request
from starlette.responses import JSONResponse

from auth.jwt_utils import login_for_access_token
from postgres.database import SessionDep
from schemas import UserLoginSchema

router = APIRouter(prefix="/api/auth", tags=["Auth"])

@router.post('/login')
async def login(login_form: UserLoginSchema, session: SessionDep):
    return await login_for_access_token(username=login_form.username, password=login_form.password, session=session)