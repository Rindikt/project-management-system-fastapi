from datetime import datetime, date
import enum

from sqlalchemy import Integer, DateTime, ForeignKey, String, Enum as SQLEnum, func, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class TaskStatus(str, enum.Enum):
    todo = 'todo'
    in_progress = 'in_progress'
    blocked = 'blocked'
    done = 'done'

class TaskPriority(str, enum.Enum):
    low = 'low'
    medium = 'medium'
    high = 'high'

class Task(Base):
    __tablename__ = 'tasks'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey('projects.id'))
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[TaskStatus] = mapped_column(
        SQLEnum(TaskStatus, name='task_status', create_type=True),
                default=TaskStatus.todo)
    priority: Mapped[TaskPriority] = mapped_column(
        SQLEnum(TaskPriority, name='task_priority', create_type=True),
                nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),server_default=func.now(), nullable=False)
    assigned_to_id: Mapped[int|None] = mapped_column(Integer, ForeignKey('users.id'), nullable=True)
    author_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    due_date: Mapped[date|None] = mapped_column(Date, nullable=True)

    project: Mapped['Project'] = relationship('Project', back_populates='tasks')
    assigned_to: Mapped['User'] = relationship(
        'User',
        foreign_keys=[assigned_to_id],
        back_populates='assigned_tasks')

    author: Mapped['User'] = relationship(
        'User',
        foreign_keys=[author_id],
        back_populates='created_tasks'
    )

