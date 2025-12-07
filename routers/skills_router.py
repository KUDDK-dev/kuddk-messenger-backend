from fastapi import APIRouter, HTTPException, Depends
from pydantic import ValidationError
from sqlalchemy import select

from auth.auth_utils import require_role
from postgres.database import SessionDep

from postgres.models import EventModel, InterestModel, SkillModel, UserModel
from schemas import SkillEditSchema, SkillAddSchema
from templates.response_templates import get_response_template

router = APIRouter(prefix="/api/skills", tags=["Skills"])

@router.post('')
async def add_skill(
        data: SkillAddSchema,
        session: SessionDep,
        user = Depends(require_role("ADMIN"))
):
    new_skill = SkillModel(
        title = data.title
    )

    session.add(new_skill)
    await session.commit()

    return get_response_template(200, "Skill has been added successfully!")

@router.get('/{skill_id}')
async def get_skill(skill_id: int, session: SessionDep):
    query = select(SkillModel).where(SkillModel.id == skill_id)
    result = await session.execute(query)

    return result.scalars().first()

@router.get('')
async def get_skills(session: SessionDep):
    query = select(SkillModel)
    result = await session.execute(query)

    return result.scalars().all()

@router.delete("/{skill_id}")
async def delete_skill(
        skill_id: int,
        session: SessionDep,
        user = Depends(require_role("ADMIN"))
):
    skill = await session.get(SkillModel, skill_id)

    if not skill:
        raise HTTPException(404, "Skill not found")

    await session.delete(skill)
    await session.commit()

    return get_response_template(202, "Skill has been deleted successfully!")

@router.put('/{skill_id}')
async def edit_skill(
        skill_id: int,
        data: SkillEditSchema,
        session: SessionDep,
        user = Depends(require_role("ADMIN"))
):
    skill = await session.get(SkillModel, skill_id)

    if not skill:
        raise HTTPException(404, "Skill not found")

    skill.title = data.title
    await session.commit()

    return get_response_template(200, "Skill has been updated successfully!")