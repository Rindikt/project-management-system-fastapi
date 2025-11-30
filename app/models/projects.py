from datetime import datetime, date

from sqlalchemy import Integer, String, ForeignKey, DateTime, func, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Project(Base):
    __tablename__ = "projects"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str|None] = mapped_column(String, nullable=True)
    owner_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    is_active: Mapped[bool] = mapped_column(default=True)
    tasks: Mapped[list['Task']] = relationship('Task', back_populates='project')
    owner: Mapped['User'] = relationship('User', back_populates='owned_projects')
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(),onupdate=func.now(), nullable=False)
    dub_date: Mapped[date|None] = mapped_column(Date, nullable=True)

    members_association: Mapped[list['ProjectMember']] = relationship(
        'ProjectMember', back_populates='project', cascade="all, delete-orphan"
    )

    members: Mapped[list['User']] = relationship(
        'User',
        secondary='project_members',
        back_populates='projects',
    )


class ProjectMember(Base):
    __tablename__ = "project_members"
    project_id: Mapped[int] = mapped_column(ForeignKey('projects.id'), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), primary_key=True)

    project: Mapped['Project'] = relationship('Project', back_populates='members_association')
    member: Mapped['User'] = relationship('User', back_populates='projects_association')





