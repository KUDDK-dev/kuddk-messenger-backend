from tokenize import String
from typing import Optional, List

from pydantic import BaseModel, Field
from sqlalchemy import UniqueConstraint, ForeignKey
from sqlalchemy.orm import mapped_column, relationship, Mapped

from postgres.models import UserModel, users_skills, users_interests, users_looking_for, events_members, users_roles
from schemas import Base


class UserDtoModel(BaseModel):
    id: int
    username: str
    first_name: str
    last_name: str
    bio: Optional[str] = None
    status: Optional[str] = None

    class Config:
        from_attributes = True

def convert_user_to_dto(user: UserModel):
    user_dict = {
        "id": user.id,
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "bio": user.bio,
        "status": user.status.name,
        "skills": user.skills,
        "interests": user.interests,
        "looking_for": user.looking_for
    }

    return UserDtoModel(**user_dict)

def convert_users_to_dtos(users: list):
    return list(map(convert_user_to_dto, users))