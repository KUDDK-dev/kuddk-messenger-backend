from fastapi import APIRouter, HTTPException, Depends
from pydantic import ValidationError
from sqlalchemy import select

from auth.auth_utils import require_role
from postgres.database import SessionDep

from postgres.models import EventModel, InterestModel, SkillModel, UserModel, StatusModel
from schemas import StatusEditSchema, StatusAddSchema
from templates.response_templates import get_response_template

router = APIRouter(prefix="/api/statuses", tags=["Statuses"])

@router.post('')
async def add_status(
        data: StatusAddSchema,
        session: SessionDep,
        user = Depends(require_role("ADMIN"))
):
    new_status = StatusModel(
        name = data.name
    )

    session.add(new_status)
    await session.commit()

    return get_response_template(200, "Status has been added successfully!")

@router.get('/{status_id}')
async def get_status(status_id: int, session: SessionDep):
    query = select(SkillModel).where(StatusModel.id == status_id)
    result = await session.execute(query)

    return result.scalars().first()

@router.get('')
async def get_statuses(session: SessionDep):
    query = select(StatusModel)
    result = await session.execute(query)

    return result.scalars().all()

@router.delete("/{status_id}")
async def delete_status(
        status_id: int,
        session: SessionDep,
        user = Depends(require_role("ADMIN"))
):
    skill = await session.get(StatusModel, status_id)

    if not skill:
        raise HTTPException(404, "Status is not found")

    await session.delete(skill)
    await session.commit()

    return get_response_template(202, "Status has been deleted successfully!")

@router.put('/{status_id}')
async def edit_status(
        status_id: int,
        data: StatusEditSchema,
        session: SessionDep,
        user = Depends(require_role("ADMIN"))
):
    skill = await session.get(SkillModel, status_id)

    if not skill:
        raise HTTPException(404, "Status is not found")

    skill.title = data.title
    await session.commit()

    return get_response_template(200, "Status has been updated successfully!")