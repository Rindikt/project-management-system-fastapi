// js/users.js

document.addEventListener('DOMContentLoaded', () => {
    // 1. Проверяем токен при загрузке страницы
    const ACCESS_TOKEN = localStorage.getItem('access_token');
    if (!ACCESS_TOKEN) {
        // Если нет токена, перенаправляем на главную
        window.location.href = 'index.html';
        return;
    }

    // 2. Инициализируем элементы
    const usersListContainer = document.getElementById('users-list-container');
    const logoutButton = document.getElementById('logout-button');

    // 3. Обработчик выхода
    logoutButton.addEventListener('click', () => {
        localStorage.clear();
        window.location.href = 'index.html';
    });

    // 4. Основная функция: Получение и отображение пользователей
    async function fetchUsers() {
        usersListContainer.innerHTML = '<p class="text-gray-500">Загрузка списка пользователей...</p>';

        try {
            const response = await fetch('http://127.0.0.1:8000/users/', {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${ACCESS_TOKEN}`,
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                // Обработка ошибки 401, 404 и т.д.
                throw new Error(`Ошибка HTTP: ${response.status}`);
            }

            const users = await response.json();

            if (users.length === 0) {
                usersListContainer.innerHTML = '<p class="text-gray-500">Пользователи не найдены.</p>';
                return;
            }

            // 5. Построение таблицы
            let tableHTML = `
                <table class="min-w-full divide-y divide-gray-200">
                    <thead class="bg-gray-50">
                        <tr>
                            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Имя и Фамилия
                            </th>
                            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Email
                            </th>
                            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Роль
                            </th>
                            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Должность
                            </th>
                        </tr>
                    </thead>
                    <tbody class="bg-white divide-y divide-gray-200">
            `;

            users.forEach(user => {
                const fullName = `${user.first_name} ${user.last_name}`;
                // Элемент становится кликабельным и ведет на user_detail.html?id=X
                const profileLink = `user_detail.html?id=${user.id}`;

                tableHTML += `
                    <tr class="user-row">
                        <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-indigo-600">
                            <a href="${profileLink}" class="hover:text-indigo-800 transition-colors">${fullName}</a>
                        </td>
                        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            ${user.email}
                        </td>
                        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 capitalize">
                            ${user.role}
                        </td>
                        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            ${user.position || '—'}
                        </td>
                    </tr>
                `;
            });

            tableHTML += `
                    </tbody>
                </table>
            `;

            usersListContainer.innerHTML = tableHTML;

        } catch (error) {
            console.error('Ошибка при получении пользователей:', error);
            usersListContainer.innerHTML = `
                <div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
                    <strong class="font-bold">Ошибка!</strong>
                    <span class="block sm:inline"> Не удалось загрузить список пользователей. Возможно, сервер недоступен или требуется повторный вход.</span>
                    <p class="text-xs mt-1">Детали: ${error.message}</p>
                </div>
            `;
        }
    }

    fetchUsers();
});