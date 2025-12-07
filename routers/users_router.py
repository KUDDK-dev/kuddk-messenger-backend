import base64
from http.client import HTTPException

from fastapi import APIRouter, Depends
from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from auth.auth_utils import require_role
from auth.jwt_utils import get_current_user, hash_password
from postgres.database import SessionDep
from postgres.dtos.user_dto import convert_user_to_dto, convert_users_to_dtos

from postgres.models import UserModel, InterestModel, SkillModel, RoleModel, StatusModel
from schemas import UserAddSchema, UserEditSchema
from templates.response_templates import get_response_template

router = APIRouter(prefix="/api/users", tags=["Users"])

# method is deprecated
@router.post('')
async def add_user(
        data: UserAddSchema,
        session: SessionDep,
        user = Depends(require_role("ADMIN"))
):
    query = select(UserModel).where(UserModel.username == data.username)
    result = await session.execute(query)

    user_or_none = result.scalar_one_or_none()

    if user_or_none:
        raise HTTPException(409, "User already exists!")

    new_user = UserModel(
        username = data.username,
        password = hash_password(data.password),
        first_name = data.first_name,
        last_name = data.last_name,
        bio = data.bio
    )

    new_user.skills = (
        await session.execute(
            select(SkillModel).where(SkillModel.title.in_(data.skills))
        )
    ).scalars().all()

    new_user.interests = (
        await session.execute(
            select(InterestModel).where(InterestModel.title.in_(data.interests))
        )
    ).scalars().all()

    new_user.looking_for = (
        await session.execute(
            select(SkillModel).where(SkillModel.title.in_(data.looking_for))
        )
    ).scalars().all()

    new_user.status = (
        await session.execute(
            select(StatusModel).where(StatusModel.name == data.status)
        )
    ).scalar_one_or_none()

    roles = set(data.roles + ['DEFAULT'])

    new_user.roles = (
        await session.execute(
            select(RoleModel).where(RoleModel.name.in_(roles))
        )
    ).scalars().all()

    session.add(new_user)
    await session.commit()

    return get_response_template(200, "User has been added successfully!")

# @router.get('/test')
# async def test(
#     user = Depends(require_role("ADMIN"))
# ):
#     return {"msg": "ok", "user": user}

@router.get('')
async def get_users(session: SessionDep):
    query = select(UserModel).options(
        selectinload(UserModel.status),
        selectinload(UserModel.skills),
        selectinload(UserModel.interests),
        selectinload(UserModel.looking_for),
        selectinload(UserModel.events),
        selectinload(UserModel.roles)
    )

    result = await session.execute(query)
    users = result.scalars().all()

    return convert_users_to_dtos(users)

@router.get('/{user_id}')
async def get_user(user_id: int, session: SessionDep):
    query = select(UserModel).where(UserModel.id == user_id)
    result = await session.execute(query)

    return convert_user_to_dto(result.scalars().first())

@router.put('/{user_id}')
async def edit_user(
        user_id: int,
        data: UserEditSchema,
        session: SessionDep,
        user = Depends(require_role("DEFAULT", "ADMIN"))
):
    user = await session.get(UserModel, user_id)

    if "ADMIN" not in [role.name for role in user.roles] and user.id != user_id:
        raise HTTPException(403, "You are not allowed to edit this user!")

    if not user:
        raise HTTPException(404, "User not found")

    query = select(UserModel).where(UserModel.username == data.username)
    result = await session.execute(query)

    user_or_none = result.scalar_one_or_none()

    if user_or_none and user_or_none.username != data.username:
        raise HTTPException(409, "User already exists!")

    user.username = data.username
    user.first_name = data.first_name
    user.last_name = data.last_name
    user.bio = data.bio

    user.roles = (
        await session.execute(
            select(RoleModel).where(RoleModel.name.in_(data.roles))
        )
    ).scalars().all()

    user.skills = (
        await session.execute(
            select(SkillModel).where(SkillModel.title.in_(data.skills))
        )
    ).scalars().all()

    user.interests = (
        await session.execute(
            select(InterestModel).where(InterestModel.title.in_(data.interests))
        )
    ).scalars().all()

    user.looking_for = (
        await session.execute(
            select(SkillModel).where(SkillModel.title.in_(data.looking_for))
        )
    ).scalars().all()

    user.status = (
        await session.execute(
            select(StatusModel).where(StatusModel.name == data.status)
        )
    ).scalar_one_or_none()

    await session.commit()

    return get_response_template(200, "User has been updated successfully!")

@router.delete("/{user_id}")
async def delete_user(
        user_id: int,
        session: SessionDep,
        user = Depends(require_role("ADMIN"))
):
    user = await session.get(UserModel, user_id)

    if not user:
        raise HTTPException(404, "User not found")

    await session.delete(user)
    await session.commit()

    return get_response_template(202, "User has been deleted successfully!")