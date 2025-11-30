from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_

from sqlalchemy.orm import selectinload

from app.models import Project
from app.models.tasks import Task, TaskPriority, TaskStatus
from app.models.users import User as UserModel, UserRole, User
from app.schemas.tasks import TaskCreate, TaskUpdate


class TaskService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_task(
            self, project_id, task: TaskCreate,
            current_user: UserModel):

        db_project = await self.db.scalar(
            select(Project)
            .options(selectinload(Project.members), selectinload(Project.owner))
            .where(Project.id == project_id)
        )
        if not db_project:
            raise ValueError(f"Проект с ID {project_id} не найден.")

        is_creator_member_or_owner = (db_project.owner_id == current_user.id or
                              any(member.id == current_user.id for member in db_project.members))

        if not is_creator_member_or_owner:
            raise PermissionError("Только владелец или участник проекта может создавать задачи в этом проекте.")

        task_data = task.model_dump()
        assigned_to_id: Optional[int] = None
        assigned_to_email = task.assigned_to_email

        if assigned_to_email is not None:
            assigned_user: Optional[UserModel] = None

            if db_project.owner.email == assigned_to_email:
                assigned_user = db_project.owner
            else:
                assigned_user = next((member for member in db_project.members if member.email == assigned_to_email),
                None)
            if assigned_user is None:
                raise ValueError("Назначенный исполнитель не является участником этого проекта.")
            assigned_to_id = assigned_user.id
        task_data = task.model_dump()
        if 'assigned_to_email' in task_data:
            del task_data['assigned_to_email']

        new_task = Task(
            **task_data,
            project_id = db_project.id,
            author_id = current_user.id,
            assigned_to_id=assigned_to_id
        )
        self.db.add(new_task)
        await self.db.commit()
        await self.db.refresh(new_task)

        loaded_task = await self.db.scalar(
            select(Task).where(Task.id == new_task.id)
            .options(selectinload(Task.project),
                     selectinload(Task.assigned_to)),
        )
        return loaded_task

    async def get_project_tasks(self, project_id:int,
                                current_user:UserModel,
                                status_filter: Optional[TaskStatus],
                                priority_filter: Optional[TaskPriority]):
        """
        Получает список задач проекта. Доступ: owner, member, admin или manager.
        """
        db_project = await self.db.scalar(
            select(Project)
            .options(selectinload(Project.members))
            .where(Project.id == project_id)
        )
        if db_project is None:
            raise ValueError(f'Проект с ID {project_id} не найден.')

        workers_in = any(member.id == current_user.id for member in db_project.members)
        is_project_owner = db_project.owner_id == current_user.id
        big_worker = current_user.role == UserRole.admin or current_user.role == UserRole.manager

        if not (is_project_owner or big_worker or workers_in):
            raise PermissionError('У вас нет прав на просмотр этих данных')

        stmt = (
            select(Task)
            .where(Task.project_id==project_id)
            .options(selectinload(Task.assigned_to),
                     selectinload(Task.project),
                     selectinload(Task.author))
            .order_by(Task.created_at.desc())
        )
        if status_filter is not None:
            stmt = stmt.where(Task.status == status_filter)
        if priority_filter is not None:
            stmt = stmt.where(Task.priority == priority_filter)

        tasks = (await self.db.scalars(stmt)).all()
        return tasks


    async def update_task(self, task_id, task: TaskUpdate,
                          current_user: UserModel)->Task:
        db_task = await self.db.scalar(
            select(Task)
            .options(selectinload(Task.project).selectinload(Project.owner),
                     selectinload(Task.assigned_to),
                     selectinload(Task.author))
            .where(Task.id == task_id))

        if db_task is None:
            raise ValueError(f'Задача с ID {task_id} не найдена.')

        db_project = db_task.project

        is_project_owner = db_task.project.owner_id == current_user.id
        is_assignee = db_task.assigned_to_id == current_user.id
        is_author = db_task.author_id == current_user.id

        if not is_project_owner and not is_assignee and not is_author:
            raise PermissionError("У вас нет прав на редактирование этой задачи."
                                  "Только владелец проекта, автор или исполнитель.")


        update_data = task.model_dump(exclude_unset=True)
        new_assigned_to_id = update_data.get('assigned_to_id')

        if new_assigned_to_id in update_data:
            if new_assigned_to_id == 0:
                update_data['assigned_to_id'] = None
                new_assigned_to_id = None
            if new_assigned_to_id is not None:
                assigned_is_member = (db_project.owner_id == new_assigned_to_id or
                                      any(member.id == new_assigned_to_id for member in db_project.members))
                if not assigned_is_member:
                    raise ValueError("Новый назначенный исполнитель не является участником этого проекта.")

        for key, value in update_data.items():
            setattr(db_task, key, value)

        await self.db.commit()
        await self.db.refresh(db_task)
        loaded_task = await self.db.scalar(
            select(Task).where(Task.id == db_task.id)
            .options(selectinload(Task.project),
                     selectinload(Task.assigned_to),
                     selectinload(Task.author)),
        )
        return loaded_task

    async def delete_task(self, task_id:int, current_user: UserModel):
        db_task = await self.db.scalar(
            select(Task)
            .options(selectinload(Task.assigned_to),
                     selectinload(Task.project))
            .where(Task.id == task_id))
        if db_task is None:
            raise ValueError(f'Задача с ID {task_id} не найдена.')
        is_author = (current_user.id == db_task.author_id)
        is_admin = current_user.role == UserRole.admin

        is_project_owner = db_task.project.owner_id == current_user.id
        if not(is_author or is_project_owner or is_admin):
            raise PermissionError("У вас нет прав на удаление этой задачи."
                                  "Только владелец проекта или автор могут её удалить.")

        await self.db.delete(db_task)
        await self.db.commit()
        return

    async def get_task_by_id(self, task_id:int, current_user:UserModel):
        db_task = await self.db.scalar(
            select(Task).options(selectinload(Task.project).selectinload(Project.members),
                                 selectinload(Task.assigned_to),
                                 selectinload(Task.author)
                                 )
            .where(Task.id == task_id)
        )

        if db_task is None:
            raise ValueError(f'Задача с ID {task_id} не найдена.')

        db_project = db_task.project

        is_project_owner = db_task.project.owner_id == current_user.id
        is_project_member = any(member.id == current_user.id for member in db_project.members)
        is_admin = current_user.role == UserRole.admin

        if is_admin:
            return db_task

        if not (is_project_owner or is_project_member):
            raise PermissionError("У вас нет прав на просмотр этой задачи.")

        return db_task

    async def get_my_assigned_tasks(self, current_user: UserModel):
        """
        Получает список задач, назначенных текущему пользователю.
        """
        stmt = (
            select(Task)
            .options(selectinload(Task.project),
                     selectinload(Task.assigned_to),
                     selectinload(Task.author))
            .where(Task.assigned_to_id == current_user.id)
            .order_by(Task.created_at.desc())
        )
        tasks = (await self.db.scalars(stmt)).all()
        return list(tasks)

    async def get_user_tasks(self, user_id, current_user: UserModel):
        """
         Получает список задач, назначенных целевому пользователю (user_id).
         Возвращает только те задачи, к проектам которых current_user имеет доступ.
         """
        task_assignment_condition = Task.assigned_to_id == user_id
        access_condition = or_(
            Project.owner_id == current_user.id,
            Project.members.any(UserModel.id == current_user.id)
        )

        stmt = (
            select(Task)
            .join(Task.project)
            .options(
                selectinload(Task.project),
                selectinload(Task.assigned_to),
                selectinload(Task.author),
            )
            .where(task_assignment_condition, access_condition)
            .order_by(Task.created_at.desc())
        )

        tasks = (await self.db.scalars(stmt)).all()
        return list(tasks)







