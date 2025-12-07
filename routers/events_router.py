from datetime import datetime, timezone
from http.client import HTTPException
from typing import Optional

from fastapi import APIRouter, Query, Depends
from pydantic import ValidationError
from sqlalchemy import select

from auth.auth_utils import require_role
from postgres.database import SessionDep

from postgres.models import EventModel, InterestModel, SkillModel, UserModel
from schemas import EventAddSchema, EventEditSchema, EventGetSchema
from templates.response_templates import get_response_template

router = APIRouter(prefix="/api/events", tags=["Events"])

@router.post('')
async def add_event(
        data: EventAddSchema,
        session: SessionDep,
        user = Depends(require_role("ADMIN"))
):
    members = []

    if data.members:
        members_objects = await session.execute(
            select(UserModel).where(UserModel.id.in_(data.members))
        )
        members = members_objects.scalars().all()

    new_event = EventModel(
        title=data.title,
        description=data.description,
        tags=data.tags,
        members=members,
        date=datetime.fromisoformat(data.date).astimezone(timezone.utc).replace(tzinfo=None)
    )

    session.add(new_event)
    await session.commit()

    return get_response_template(200, "Event has been added successfully!")

@router.get("")
async def get_events(
    session: SessionDep,
    start_date: Optional[int] = Query(None, description="Начальная дата в Unix timestamp"),
    end_date: Optional[int] = Query(None, description="Конечная дата в Unix timestamp")
):
    stmt = select(EventModel)

    if start_date:
        start_datetime = datetime.fromtimestamp(start_date)
        stmt = stmt.where(EventModel.date >= start_datetime)

    if end_date:
        end_datetime = datetime.fromtimestamp(end_date)
        stmt = stmt.where(EventModel.date <= end_datetime)

    stmt = stmt.order_by(EventModel.date)

    result = await session.execute(stmt)
    events = result.scalars().all()

    return events

@router.get('/{event_id}')
async def get_event(event_id: int, session: SessionDep):
    query = select(UserModel).where(EventModel.id == event_id)
    result = await session.execute(query)

    return result.scalars().first()

@router.put('/{event_id}')
async def edit_event(
        event_id: int,
        data: EventEditSchema,
        session: SessionDep,
        user = Depends(require_role("ADMIN"))
):
    event = await session.get(EventModel, event_id)

    if not event:
        raise HTTPException(404, "Event not found")

    event.title = data.title
    event.description = data.description
    event.date = data.date

    event.members = (
        await session.execute(
            select(UserModel).where(UserModel.id.in_(data.members))
        )
    ).scalars().all()

    event.tags = (
        await session.execute(
            select(InterestModel).where(InterestModel.title.in_(data.tags))
        )
    ).scalars().all()

    await session.commit()

    return get_response_template(200, "Event has been updated successfully!")

@router.delete("/{event_id}")
async def delete_event(
        event_id: int,
        session: SessionDep,
        user = Depends(require_role("ADMIN"))
):
    event = await session.get(EventModel, event_id)

    if not event:
        raise HTTPException(404, "Event not found")

    await session.delete(event)
    await session.commit()

    return get_response_template(202, "Event has been deleted successfully!")