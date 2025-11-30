import enum

from sqlalchemy import Integer, String, Enum as SQLEnum, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class UserRole(enum.Enum):
    owner = "owner"
    member = "member"
    manager = "manager"
    admin = "admin"

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    first_name: Mapped[str] = mapped_column(String, nullable=False)
    last_name: Mapped[str] = mapped_column(String, nullable=False)
    position: Mapped[str] = mapped_column(String, nullable=True)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[UserRole] = mapped_column(
        SQLEnum(UserRole, name="user_role_enum", create_type=True),
        default=UserRole.member)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    assigned_tasks: Mapped[list['Task']] = relationship(
        'Task',
        foreign_keys="[Task.assigned_to_id]",
        back_populates='assigned_to')
    owned_projects: Mapped[list['Project']] = relationship(
        'Project', back_populates='owner', foreign_keys="[Project.owner_id]")

    projects_association: Mapped[list['ProjectMember']] = relationship(
        'ProjectMember', back_populates='member', cascade="all, delete-orphan")

    projects: Mapped[list['Project']] = relationship(
        'Project',
        secondary='project_members',
        back_populates='members'
    )
    created_tasks: Mapped[list['Task']] = relationship(
        'Task',
        back_populates='author',
        foreign_keys='[Task.author_id]'
    )
