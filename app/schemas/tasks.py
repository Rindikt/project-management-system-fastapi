from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict, field_validator
from app.models.tasks import TaskStatus, TaskPriority


class TaskCreate(BaseModel):
    """
    Схема для создания задачи.
    """
    title: str = Field(..., max_length=80, description='Название задачи')
    description: str = Field(..., min_length=10, max_length=500, description='Описание задачи')
    priority: TaskPriority = Field(..., description='Приоритет задачи')
    due_date: date|None = Field(None,description='Дата дедлайна')
    assigned_to_email: Optional[str] = Field(None, description='email работника')


class TaskUpdate(BaseModel):
    """
    Схема для обновления задачи.
    """
    title: Optional[str] = Field(None, max_length=80, description='Название задачи')
    description: Optional[str] = Field(None, min_length=10, max_length=500, description='Описание задачи')
    priority: Optional[TaskPriority] = Field(None, description='Приоритет задачи')
    due_date: date | None = Field(None, description='Дата дедлайна')
    status: Optional[TaskStatus] = Field(None, description='Статус задачи')
    assigned_to_email: Optional[str] = Field(None, description='email работника')


class TaskRead(BaseModel):
    """
    Схема для просмотра задачи.
    """
    id: int = Field(description='ID задачи')
    project: 'ProjectBasic' = Field(description='ID проекта')
    project_id: int = Field(description='ID проекта, к которому относится задача')
    title: str = Field(description='Название задачи')
    description: str = Field(description='Описание задачи')
    status: TaskStatus = Field(description='Статус задачи')
    priority: TaskPriority = Field(description='Приоритет задачи')
    created_at: datetime = Field(description='Дата создания задачи')
    due_date: date|None = Field(None, description='Дата дедлайна')

    assigned_to: 'UserBasicSchema | None' = Field(None, description='Ответственный за задачу')
    author: 'UserBasicSchema'
    model_config = ConfigDict(from_attributes=True)

    @field_validator('due_date', mode='before')
    @classmethod
    def convert_datetime_to_date(cls, value):
        """Конвертирует datetime, полученный из ORM, в date, если это необходимо."""
        if isinstance(value, datetime):
            if value is None:
                return None
            # Извлекаем только дату, отбрасывая временную часть
            return value.date()
        return value

class TaskList(BaseModel):
    """
    Список пагинации для задач.
    """
    items: list[TaskRead] = Field(description='Список задач')

