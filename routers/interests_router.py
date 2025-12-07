from fastapi import APIRouter, HTTPException, Depends
from pydantic import ValidationError
from sqlalchemy import select

from auth.auth_utils import require_role
from postgres.database import SessionDep

from postgres.models import EventModel, InterestModel, SkillModel, UserModel
from schemas import InterestEditSchema, InterestAddSchema
from templates.response_templates import get_response_template

router = APIRouter(prefix="/api/interests", tags=["Intrests"])

@router.post('')
async def add_interest(
        data: InterestAddSchema,
        session: SessionDep,
        user = Depends(require_role("ADMIN"))
):
    new_interest = InterestModel(
        title = data.title
    )

    session.add(new_interest)
    await session.commit()

    return get_response_template(200, "Interest has been added successfully!")

@router.get('/{interest_id}')
async def get_interest(interest_id: int, session: SessionDep):
    query = select(InterestModel).where(InterestModel.id == interest_id)
    result = await session.execute(query)

    return result.scalars().first()

@router.get('')
async def get_interests(session: SessionDep):
    query = select(InterestModel)
    result = await session.execute(query)

    return result.scalars().all()

@router.delete("/{interest_id}")
async def delete_interest(
        interest_id: int,
        session: SessionDep,
        user = Depends(require_role("ADMIN"))
):
    interest = await session.get(SkillModel, interest_id)

    if not interest:
        raise HTTPException(404, "Interest is not found")

    await session.delete(interest)
    await session.commit()

    return get_response_template(202, "Interest has been deleted successfully!")

@router.put('/{interest_id}')
async def edit_interest(
        interest_id: int,
        data: InterestEditSchema,
        session: SessionDep,
        user = Depends(require_role("ADMIN"))
):
    interest = await session.get(SkillModel, interest_id)

    if not interest:
        raise HTTPException(404, "Interest is not found")

    interest.title = data.title
    await session.commit()

    return get_response_template(200, "Interest has been updated successfully!")