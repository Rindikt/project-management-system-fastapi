from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_owner, get_current_member
from app.models.users import User as UserModel
from app.db_depends import get_async_db
from app.schemas.projects import (
    ProjectCreate as ProjectSchema,
    ProjectRead as ProjectReadSchema,
    ProjectListSchema,
    ProjectUpdate,)
from app.services.project_service import ProjectService
router = APIRouter(
    prefix="/projects",
    tags=["projects"]
)

@router.get("/", response_model=list[ProjectListSchema])
async def get_projects(
        db: AsyncSession = Depends(get_async_db),
        current_user: UserModel = Depends(get_current_member),
        only_owned: bool = False):
    """
    Позволяет искать проекты по названию, статусу или владельцу.
    """
    project_service = ProjectService(db)
    projects = await project_service.get_projects(
        current_user=current_user,
        only_owned=only_owned
    )
    return projects

@router.get("/{project_id}", response_model=ProjectReadSchema)
async def get_project(project_id: int,
                      db: AsyncSession = Depends(get_async_db),
                      current_user: UserModel = Depends(get_current_member)):
    project_service = ProjectService(db=db)
    try:
        project = await project_service.get_project(project_id, current_user)
        return project
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))



@router.post('/', response_model=ProjectReadSchema, status_code=status.HTTP_201_CREATED)
async def create_project(project: ProjectSchema,
                         db: AsyncSession = Depends(get_async_db),
                         current_user: UserModel = Depends(get_current_owner)):
    """
    Обрабатывает HTTP-запрос на создание проекта.
    """
    project_service = ProjectService(db=db)
    return await project_service.create_project(project, current_user)


@router.patch('/{project_id}', response_model=ProjectReadSchema)
async def update_project(project_id: int,
                         project_in: ProjectUpdate,
                         current_user: UserModel = Depends(get_current_owner),
                         db: AsyncSession = Depends(get_async_db)):

    project_service = ProjectService(db=db)

    try:
        project = await project_service.update_project(project_id, project_in, current_user)
        return project
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Произошла непредвиденная ошибка при обновлении проекта.")

@router.post('/{project_id}/members/{email}',
             response_model=ProjectReadSchema,
             status_code=status.HTTP_201_CREATED, tags=['Members'])
async def add_member_to_project(project_id: int,
                                email: str,
                                db: AsyncSession = Depends(get_async_db),
                                current_owner: UserModel = Depends(get_current_owner))->ProjectReadSchema:
    """
    Добавляет пользователя с user_id в проект project_id. Только для владельца проекта.
    """
    project_service = ProjectService(db=db)
    try:
        project = await project_service.add_member(project_id, email, current_owner)
        return project
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete('/{project_id}/members/{user_id}', response_model=ProjectReadSchema)
async def remove_member_from_project(
        project_id: int, user_id: int,
        db: AsyncSession = Depends(get_async_db),
        current_user: UserModel = Depends(get_current_owner)):
    """
    Удаляет пользователя с user_id из проекта project_id. Только для владельца проекта.
    """

    project_service = ProjectService(db=db)

    try:
        result = await project_service.remove_member(project_id, user_id, current_user)
        return result
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.delete('/{project_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(project_id: int,
                         db: AsyncSession = Depends(get_async_db),
                         current_user: UserModel = Depends(get_current_owner)):

    project_service = ProjectService(db=db)
    try:
        await project_service.delete_project(project_id=project_id,
                                                       current_user=current_user)
        return {'message': f'Проект {project_id} был удален.'}

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
