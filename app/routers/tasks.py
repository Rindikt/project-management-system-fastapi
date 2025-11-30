from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_member, get_current_user
from app.models.users import User as UserModel
from app.db_depends import get_async_db
from app.schemas.tasks import TaskCreate, TaskRead, TaskList, TaskUpdate
from app.services.task_service import TaskService
from app.models.tasks import TaskStatus, TaskPriority

router_project_tasks = APIRouter(
    tags=["tasks"]
)

router_global_tasks = APIRouter(
    prefix="/tasks",
    tags=["tasks"]
)

@router_project_tasks.get('/{project_id}/tasks/', response_model=TaskList)
async def get_tasks_list(
    project_id: int,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
    status_filter: Optional[TaskStatus] =Query(None, description='Фильтр по статусу задачи'),
    priority_filter: Optional[TaskPriority] = Query(None, description='Фильтр по приоритету задачи')):
    """
    Список задач проекта. Фильтрация по status и priority. Доступ только если пользователь owner ИЛИ member проекта.
    """

    task_service = TaskService(db=db)

    try:
        result = await task_service.get_project_tasks(
            project_id,
            status_filter=status_filter,
            priority_filter=priority_filter,
            current_user=current_user)
        return {'items': result}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router_global_tasks.get('/{task_id}', response_model=TaskRead)
async def get_task(task_id: int,
                    db: AsyncSession = Depends(get_async_db),
                    current_user: UserModel = Depends(get_current_user)):
    task_service = TaskService(db=db)
    try:
        task = await task_service.get_task_by_id(task_id, current_user)
        return task
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router_global_tasks.get('/my', response_model=TaskList)
async def get_my_assigned_tasks(
        db: AsyncSession = Depends(get_async_db),
        current_user: UserModel = Depends(get_current_member)):
    """
    Получает список всех задач, назначенных текущему пользователю. (GET /tasks/my)
    """
    task_service = TaskService(db=db)
    try:
        task = await task_service.get_my_assigned_tasks(current_user)
        return task
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router_project_tasks.post('/{project_id}/tasks', response_model=TaskRead, status_code=status.HTTP_201_CREATED)
async def create_task(
        project_id: int, task: TaskCreate,
        db: AsyncSession=Depends(get_async_db),
        current_user: UserModel = Depends(get_current_user)
        ):
    task_service = TaskService(db=db)
    try:
        result = await task_service.create_task(
            project_id=project_id,
            task=task,
            current_user=current_user)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        )
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

@router_global_tasks.patch('/{task_id}', response_model=TaskRead)
async def update_task(task_id: int, task: TaskUpdate,
                                  current_user: UserModel = Depends(get_current_user),
                                  db: AsyncSession=Depends(get_async_db)):
    """
    Частично обновляет задачу по ID. Доступно владельцу проекта, автору задачи или исполнителю.
    """
    task_service = TaskService(db=db)
    try:
        result = await task_service.update_task(
        task_id=task_id,
        task=task,
        current_user=current_user)
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router_global_tasks.delete('/{task_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: int, db: AsyncSession=Depends(get_async_db),
                      current_user: UserModel = Depends(get_current_user)):
    task_service = TaskService(db=db)
    try:
        await task_service.delete_task(task_id, current_user)
        return {'message': 'Task deleted'}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))




