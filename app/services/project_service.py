from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload, joinedload

from app.models.users import User as UserModel, UserRole
from app.models.projects import Project
from app.schemas.projects import ProjectCreate as ProjectSchema, ProjectUpdate


class ProjectService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_project(self, project: ProjectSchema,
                             owner: UserModel):
        """
        Создает новый проект, используя данные из схемы и ID владельца.
        """
        new_project = Project(
            title=project.title,
            description=project.description,
            owner_id=owner.id,
            dub_date=project.dub_date,)
        new_project.members.append(owner)
        self.db.add(new_project)
        await self.db.commit()
        await self.db.refresh(new_project)

        stmt = (select(Project)
                .where(Project.id == new_project.id)
                .options(
            selectinload(Project.owner).selectinload(UserModel.assigned_tasks),
            selectinload(Project.tasks),
            selectinload(Project.members)
        ))
        loaded_project = await self.db.scalar(stmt)
        return loaded_project


    async def get_projects(self, current_user: UserModel,
                           only_owned: bool = False)->list[Project]:
        """
        Получает список проектов, в которых пользователь является владельцем ИЛИ членом.
        Если only_owned=True, возвращает только проекты, принадлежащие пользователю.
        """
        stmt = (
            select(Project)
            .options(
                joinedload(Project.owner),
                selectinload(Project.members),
            )
            .order_by(Project.created_at.desc())
        )
        if current_user.role == UserRole.admin:
            projects = (await self.db.scalars(stmt)).all()
            return list(projects)
        if only_owned:
            stmt = stmt.where(Project.owner_id == current_user.id)
        else:
            access_condition = or_(
                Project.owner_id == current_user.id,
                Project.members.any(UserModel.id == current_user.id)
            )
            stmt = stmt.where(access_condition)

        projects = (await self.db.scalars(stmt)).all()
        return list(projects)


    async def get_project(self, project_id: int, current_user: UserModel)->Project:
        """
        Отдает проект и проверяет членство/владение для контроля доступа.
        """
        project = await self.db.scalar(
            select(Project)
            .options(
                selectinload(Project.owner),
                selectinload(Project.tasks),
                selectinload(Project.members))
            .where(Project.id == project_id))
        if project is None:
            raise ValueError(f"Проект с ID {project_id} не найден.")

        is_admin = current_user.role == UserRole.admin
        if is_admin:
            return project

        is_owner = project.owner_id == current_user.id
        is_member = any(member.id == current_user.id for member in project.members)

        if not (is_owner or is_member):
            raise PermissionError("У вас нет доступа к этому проекту.")
        return project

    async def update_project(
            self, project_id: int,
            project: ProjectUpdate,
            owner: UserModel)->Project:
        """
        Обновляет поля в проекте.
        """
        db_project = await self.get_project(project_id, owner)

        if db_project.owner_id != owner.id:
            raise PermissionError("У вас нет прав на редактирование этого проекта.")

        if project.title is not None:
            db_project.title = project.title
        if project.description is not None:
            db_project.description = project.description
        if hasattr(project, 'dub_date'):
            db_project.dub_date = project.dub_date

        await self.db.commit()
        await self.db.refresh(db_project)
        return db_project

    async def add_member(self, project_id: int, email: str, owner: UserModel)->Project:
        """
        Добавляет участника в проект.
        """
        db_project = await self.get_project(project_id, owner)
        if db_project.owner_id != owner.id:
            raise PermissionError("У вас нет прав на добавление участников в этот проект.")

        db_user = await self.db.scalar(select(UserModel).where(UserModel.email == email))
        if db_user is None:
            raise ValueError(f"Пользователь с email {email} не найден.")
        is_member = any(member.email == email for member in db_project.members)
        if is_member:
            raise ValueError(f'Пользователь с email {email} уже учавствует в этом проекте')

        db_project.members.append(db_user)
        await self.db.commit()
        await self.db.refresh(db_project)
        return db_project

    async def remove_member(self,project_id: int, user_id: int, current_user):
        """
        Удаляет учакстника из проекта.
        """
        db_project = await self.get_project(project_id, current_user)
        if db_project.owner_id != current_user.id:
            raise PermissionError("У вас нет прав на изгнание участников из этого проекта.")
        db_user = await self.db.scalar(
            select(UserModel)
            .where(UserModel.id == user_id, UserModel.is_active == True))
        if db_user is None:
            raise ValueError(f"Пользователь с ID {user_id} не найден.")

        user_to_remove = next(
            (member for member in db_project.members if member.id == user_id),
            None
        )

        if user_to_remove is None:
            raise ValueError(f'Пользователь с ID {user_id} отсутствует в этом проекте')

        db_project.members.remove(user_to_remove)
        await self.db.commit()
        await self.db.refresh(db_project)
        return db_project

    async def delete_project(self, project_id: int, current_user:UserModel):
        """
        Удаляет проект. Доступ: только владелец проекта и админ.
        """
        project = await self.db.scalar(select(Project).where(Project.id == project_id))

        if project is None:
            raise ValueError('Проект отсутствует')

        can_delete = (project.owner_id == current_user.id or
                      current_user.role == UserRole.admin)

        if  not can_delete:
            raise PermissionError('Проект может удалить только владелец или админ')

        await self.db.delete(project)
        await self.db.commit()
        return





