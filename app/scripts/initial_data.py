import asyncio
from app.db_depends import get_async_db
from app.services.user_service import UserService
from app.models.users import UserRole  # Импортируем наш Enum


async def create_initial_users():
    """Создает первого Администратора и первого Владельца."""
    async for session in get_async_db():
        user_service = UserService(session)

        # --- 1. Создаем ADMIN ---
        try:
            admin_data = {
                'email': 'admin@company.com',
                'password': 'AdminPass123',
                'first_name': 'Global',
                'last_name': 'Admin'
            }
            await user_service.create_user_with_role(admin_data, UserRole.admin)
            print("✅ Администратор успешно создан.")
        except ValueError as e:
            print(f"⚠️ Администратор уже существует: {e}")

        # --- 2. Создаем OWNER (для создания первого проекта) ---
        try:
            owner_data = {
                'email': 'owner@company.com',
                'password': 'OwnerPass123',
                'first_name': 'Project',
                'last_name': 'Owner'
            }
            await user_service.create_user_with_role(owner_data, UserRole.owner)
            print("✅ Владелец проекта успешно создан.")
        except ValueError as e:
            print(f"⚠️ Владелец уже существует: {e}")


if __name__ == "__main__":
    # Запускаем асинхронную функцию
    asyncio.run(create_initial_users())