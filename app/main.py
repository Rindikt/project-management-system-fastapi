from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import users, projects, tasks
from app.config import settings
import app.schemas.tasks

app = FastAPI(
    title='Project Management System',
    version='1.0',
)



app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(projects.router)
app.include_router(tasks.router_project_tasks, prefix="/projects")
app.include_router(tasks.router_global_tasks)



@app.get('/')
async def root():
    """
    Корневой маршрут, подтверждающий, что API работает.
    """
    return {'message': 'Добро пожаловать в API Project Management System'}