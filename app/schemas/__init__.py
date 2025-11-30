from .users import UserRead, UserBasicSchema, UserReadSchema
from .tasks import TaskRead, TaskUpdate
from .projects import ProjectRead, ProjectListSchema,ProjectBasic

UserReadSchema.model_rebuild()
UserRead.model_rebuild()
UserBasicSchema.model_rebuild()
TaskRead.model_rebuild()
ProjectRead.model_rebuild()
ProjectListSchema.model_rebuild()