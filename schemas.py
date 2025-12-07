from typing import List, Optional

from fastapi import HTTPException, Query
from pydantic import BaseModel, EmailStr, Field, validator
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import date, datetime, time, timedelta, timezone


class Base(DeclarativeBase):
    pass


class UserAddSchema(BaseModel):
    username: str = Field(..., min_length=1, max_length=25)
    password: str = Field(..., min_length=1, max_length=25)
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    bio: Optional[str] = Field(
        None,
        min_length=1,
        max_length=200
    )

    skills: List[int] = []
    interests: List[int] = []
    looking_for: List[int] = []
    status: str
    roles: List[str] = []

class UserEditSchema(BaseModel):
    username: str = Field(..., min_length=1, max_length=25)
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    bio: Optional[str] = Field(
        None,
        min_length=1,
        max_length=200
    )

    skills: List[int] = []
    interests: List[int] = []
    looking_for: List[int] = []
    status: str
    roles: List[str] = []

class EventAddSchema(BaseModel):
    title: str = Field(..., min_length = 1, max_length = 50)
    description: str = Field(..., min_length = 1, max_length = 200)
    tags: List[str] = []
    members: List[int] = []
    date: str

    @validator('date')
    def validate_date(cls, v):
        try:
            if v.endswith('Z'):
                v = v[:-1] + '+00:00'

            dt = datetime.fromisoformat(v)

            if dt.tzinfo:
                dt = dt.astimezone(timezone.utc).replace(tzinfo=None)

            return str(dt)

        except ValueError:
            raise HTTPException(422, "Data is invalid!")

class EventEditSchema(BaseModel):
    title: str = Field(..., min_length = 1, max_length = 50)
    description: str = Field(..., min_length = 1, max_length = 200)
    tags: List[str] = []
    members: List[int] = []
    date: str

    @validator('date')
    def validate_date(cls, v):
        try:
            if v.endswith('Z'):
                v = v[:-1] + '+00:00'

            dt = datetime.fromisoformat(v)

            if dt.tzinfo:
                dt = dt.astimezone(timezone.utc).replace(tzinfo=None)

            return str(dt)

        except ValueError:
            raise HTTPException(422, "Data is invalid!")

class SkillAddSchema(BaseModel):
    title: str = Field(..., min_length = 1, max_length = 50)

class SkillEditSchema(BaseModel):
    title: str = Field(..., min_length = 1, max_length = 50)

class StatusAddSchema(BaseModel):
    title: str = Field(..., min_length=1, max_length=50)

class StatusEditSchema(BaseModel):
    title: str = Field(..., min_length=1, max_length=50)

class InterestAddSchema(BaseModel):
    title: str = Field(..., min_length = 1, max_length = 50)

class InterestEditSchema(BaseModel):
    title: str = Field(..., min_length = 1, max_length = 50)

class UserLoginSchema(BaseModel):
    username: str = Field(..., min_length=1, max_length=25)
    password: str = Field(..., min_length=1, max_length=25)

class EventGetSchema(BaseModel):
    startDate: Optional[int] = Query(None, description="Начальная дата в Unix timestamp"),
    endDate: Optional[int] = Query(None, description="Конечная дата в Unix timestamp"),

class TokenSchema(BaseModel):
    access_token: str