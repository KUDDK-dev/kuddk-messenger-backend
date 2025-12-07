from pydantic import BaseModel, EmailStr
from sqlalchemy import String, UniqueConstraint, Column, ForeignKey, Table, DateTime
from sqlalchemy.orm import mapped_column, Mapped, relationship

from schemas import Base

# class OrganizationModel(Base):
#     __tablename__ = "organizations"
#     id: Mapped[int] = mapped_column(primary_key=True)
#     name: Mapped[str] = mapped_column(String)
#     address: Mapped[str] = mapped_column(String)
#     email: Mapped[str] = mapped_column(String)

events_members = Table(
    "events_members",
    Base.metadata,
    Column("event_id", ForeignKey("events.id"), primary_key=True),
    Column("user_id", ForeignKey("users.id"), primary_key=True),
)

events_tags = Table(
    "events_tags",
    Base.metadata,
    Column("event_id", ForeignKey("events.id"), primary_key=True),
    Column("tag_id", ForeignKey("interests.id"), primary_key=True),
)

users_skills = Table(
    "users_skills",
    Base.metadata,
    Column("user_id", ForeignKey("users.id"), primary_key=True),
    Column("skill_id", ForeignKey("skills.id"), primary_key=True),
)

users_interests = Table(
    "users_interests",
    Base.metadata,
    Column("user_id", ForeignKey("users.id"), primary_key=True),
    Column("interest_id", ForeignKey("interests.id"), primary_key=True),
)

users_looking_for = Table(
    "users_looking_for",
    Base.metadata,
    Column("user_id", ForeignKey("users.id"), primary_key=True),
    Column("skill_id", ForeignKey("skills.id"), primary_key=True),
)

users_roles = Table(
    "users_roles",
    Base.metadata,
    Column("user_id", ForeignKey("users.id"), primary_key=True),
    Column("role_id", ForeignKey("roles.id"), primary_key=True),
)

class UserModel(Base):
    __tablename__ = "users"

    __table_args__ = (
        UniqueConstraint("username", name="uq_users_username"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String)
    password: Mapped[str] = mapped_column(String)
    first_name: Mapped[str] = mapped_column(String)
    last_name: Mapped[str] = mapped_column(String)
    bio: Mapped[str] = mapped_column(String)

    status_id: Mapped[int] = mapped_column(ForeignKey("statuses.id"))
    status = relationship("StatusModel", uselist=False)

    skills = relationship(
        "SkillModel",
        secondary=users_skills,
        lazy="selectin"
    )

    interests = relationship(
        "InterestModel",
        secondary=users_interests,
        lazy="selectin"
    )

    looking_for = relationship(
        "SkillModel",
        secondary=users_looking_for,
        lazy="selectin"
    )

    events = relationship(
        "EventModel",
        secondary=events_members,
        back_populates="members",
        lazy="selectin"
    )

    roles = relationship(
        "RoleModel",
        secondary=users_roles,
        back_populates="users",
        lazy="selectin"
    )

class RoleModel(Base):
    __tablename__ = "roles"

    __table_args__ = (
        UniqueConstraint("name", name="uq_roles_name"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String)

    users = relationship(
        "UserModel",
        secondary=users_roles,
        back_populates="roles",
        lazy="selectin"
    )

class EventModel(Base):
    __tablename__ = "events"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(String)
    date = Column(DateTime)

    members = relationship(
        "UserModel",
        secondary=events_members,
        back_populates="events",
        lazy="selectin"
    )

    tags = relationship(
        "InterestModel",
        secondary=events_tags,
        lazy="selectin"
    )

class SkillModel(Base):
    __tablename__ = "skills"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String)

class InterestModel(Base):
    __tablename__ = "interests"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String)

class StatusModel(Base):
    __tablename__ = "statuses"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String)

    # users = relationship("UserModel", back_populates="status")