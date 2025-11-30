from datetime import date
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class ProjectBasic(BaseModel):
    id: int
    title: str
    model_config = ConfigDict(from_attributes=True)

class ProjectCreate(BaseModel):
    """Схема для создания проекта."""
    title: str = Field(..., min_length=1, max_length=50, description='Название проекта')
    description: str = Field(..., description='Описание проекта')
    dub_date: date|None = Field(None, description='Дата дедлайна')

class ProjectUpdate(BaseModel):
    """Схема для обновления проекта."""
    title: Optional[str] = Field(None, description='Название проекта')
    description: Optional[str] = Field(None, description='Описание проекта')
    dub_date: Optional[date] = Field(None, description='Дата дедлайна')


class ProjectListSchema(BaseModel):
    id: int = Field(..., description='ID Проекта')
    title: str = Field(..., description='Название проекта')
    description: str | None = Field(None, description='Описание проекта')
    owner: 'UserReadSchema' = Field(..., description='Владелец проекта')
    model_config = ConfigDict(from_attributes=True)
    dub_date: Optional[date] = Field(None, description='Дата дедлайна')

class ProjectRead(ProjectListSchema):
    """Схема для просмотра проекта."""

    tasks: list['TaskRead'] = Field(default=list, description='Список задачь проекта')
    members: list['UserReadSchema'] = Field(
        default=list, description='Список работников учавствующих в проекте')





