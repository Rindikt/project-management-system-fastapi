// =====================================================================
// js/user_detail.js - ЛОГИКА СТРАНИЦЫ ПРОФИЛЯ (Устойчивая версия)
// =====================================================================

// --- ГЛОБАЛЬНЫЕ КОНСТАНТЫ И УТИЛИТЫ ---
const API_BASE_URL = 'http://127.0.0.1:8000';
const INDEX_PAGE = 'index.html';

let currentUserData = null;
let authUserData = null;
let ACCESS_TOKEN = localStorage.getItem('access_token');


// --- УТИЛИТЫ ---

function getStatusElement() {
    return document.getElementById('status-message');
}

function setStatus(message, isError) {
    const statusMessage = getStatusElement();
    if (!statusMessage) return;

    statusMessage.textContent = message;
    if (isError) {
        statusMessage.className = 'mt-2 p-2 rounded-lg text-sm bg-red-100 text-red-700 transition-all duration-300 min-h-6';
    } else {
        statusMessage.className = 'mt-2 p-2 rounded-lg text-sm bg-green-100 text-green-700 transition-all duration-300 min-h-6';
    }
    setTimeout(() => {
        statusMessage.textContent = '';
        statusMessage.className = 'mt-2 p-2 rounded-lg text-sm transition-all duration-300 min-h-6';
    }, 5000);
}

function handleLogout() {
    localStorage.clear();
    window.location.href = INDEX_PAGE;
}

function getUserIdFromUrl() {
    const urlParams = new URLSearchParams(window.location.search);
    const id = urlParams.get('id');
    return id ? parseInt(id, 10) : null;
}

function getAuthUserData() {
    try {
        const userDataString = localStorage.getItem('auth_user_data');
        if (userDataString) {
            const data = JSON.parse(userDataString);
            data.id = parseInt(data.id, 10);
            return data;
        }
    } catch (e) {
        console.error("Ошибка при чтении данных пользователя из localStorage:", e);
    }
    return { id: null, role: 'guest' };
}


// --- ФУНКЦИИ РЕНДЕРИНГА ---

function renderUserRelations(user) {
    const ownedProjectsList = document.getElementById('owned-projects-list');
    const assignedTasksList = document.getElementById('assigned-tasks-list');
    const tasksCountSpan = document.getElementById('tasks-count-span');

    // 1. Рендеринг Проектов (Устойчивая обработка отсутствия поля)
    ownedProjectsList && (ownedProjectsList.innerHTML = '');
    const projectsToRender = user.owned_projects || [];

    if (projectsToRender.length > 0 && ownedProjectsList) {
        projectsToRender.forEach(project => {
            const li = document.createElement('li');
            li.innerHTML = `
                <a href="project_detail.html?id=${project.id}" class="text-indigo-600 hover:text-indigo-800 transition-colors text-sm font-medium block p-1 bg-gray-50 rounded">
                    ${project.title}
                </a>
            `;
            ownedProjectsList.appendChild(li);
        });
    } else if (ownedProjectsList) {
        ownedProjectsList.innerHTML = '<li class="text-sm text-gray-500">Нет проектов в управлении.</li>';
    }

    // 2. Рендеринг Задач (Устойчивая обработка отсутствия поля)
    assignedTasksList && (assignedTasksList.innerHTML = '');
    const tasksToRender = user.assigned_tasks || user.tasks || [];

    // Устанавливаем счетчик задач
    const tasksCount = user.tasks_count !== undefined && user.tasks_count !== null
                                 ? user.tasks_count
                                 : tasksToRender.length;
    tasksCountSpan && (tasksCountSpan.textContent = tasksCount);


    if (tasksToRender.length > 0 && assignedTasksList) {
        tasksToRender.forEach(task => {
            const statusText = task.status || 'Статус не указан';

            const li = document.createElement('li');
            li.innerHTML = `
                <a href="task_detail.html?id=${task.id}" class="text-gray-700 hover:text-gray-900 transition-colors text-sm block p-1 bg-gray-50 rounded">
                    <span class="font-semibold">${task.title}</span> - ${statusText}
                </a>
            `;
            assignedTasksList.appendChild(li);
        });
    } else if (assignedTasksList) {
        assignedTasksList.innerHTML = '<li class="text-sm text-gray-500">Нет назначенных задач.</li>';
    }
}

function renderUserDetails(user) {
    currentUserData = user;

    // Безопасный поиск элементов внутри функции
    const userPageTitle = document.getElementById('user-page-title');
    const userMainTitle = document.getElementById('user-main-title');
    const userEmailView = document.getElementById('user-email-view');
    const userFirstNameView = document.getElementById('user-first-name-view');
    const userLastNameView = document.getElementById('user-last-name-view');
    const userRoleView = document.getElementById('user-role-view');
    const userPositionView = document.getElementById('user-position-view');
    const userIsActiveView = document.getElementById('user-is-active-view');
    const userIdView = document.getElementById('user-id-view');

    // 1. Заполнение основных полей (используя опциональную цепочку для безопасности)
    userPageTitle && (userPageTitle.textContent = user.first_name || user.email);

    const isActiveText = user.is_active ? 'Да' : 'Нет';
    const isActiveClass = user.is_active ? 'text-green-600 font-bold' : 'text-red-600 font-bold';

    userMainTitle && (userMainTitle.textContent = user.first_name || user.email);
    userEmailView && (userEmailView.textContent = user.email);
    userFirstNameView && (userFirstNameView.textContent = user.first_name || 'Не указано');
    userLastNameView && (userLastNameView.textContent = user.last_name || 'Не указано');
    userRoleView && (userRoleView.textContent = (user.role?.charAt(0).toUpperCase() + user.role?.slice(1)) || 'Не указана');
    userPositionView && (userPositionView.textContent = user.position || 'Не указана');

    if (userIsActiveView) {
        userIsActiveView.innerHTML = `<span class="${isActiveClass}">${isActiveText}</span>`;
    }

    userIdView && (userIdView.textContent = user.id);

    // 2. Вызываем рендеринг отношений
    renderUserRelations(user);
    checkPermissionsAndRenderButton(user);

    setStatus(`Профиль пользователя "${user.email}" успешно загружен.`, false);
}


// --- ПРОВЕРКА ПРАВ ---

function checkPermissionsAndRenderButton(viewedUser) {
    authUserData = getAuthUserData();
    const editUserBtn = document.getElementById('edit-user-btn');

    if (!editUserBtn) return;

    const isSelf = authUserData.id === viewedUser.id;
    const isAdmin = authUserData.role === 'admin';

    if (isSelf || isAdmin) {
        editUserBtn.classList.remove('hidden');
        editUserBtn.onclick = null;
        editUserBtn.addEventListener('click', () => openEditUserForm(viewedUser));
    } else {
        editUserBtn.classList.add('hidden');
    }
}


// --- ОСНОВНАЯ ЛОГИКА ЗАГРУЗКИ ---

async function fetchUserDetail() {
    let accessToken = localStorage.getItem('access_token');
    const userIdFromUrl = getUserIdFromUrl();

    if (!accessToken) {
        handleLogout();
        return;
    }

    let fetchUrl = `${API_BASE_URL}/users/`;

    // Определяем, какой путь использовать: /users/{id} или /users/me
    if (userIdFromUrl) {
        fetchUrl += `${userIdFromUrl}`;
    } else {
        fetchUrl += `me`;
    }

    try {
        const response = await fetch(fetchUrl, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${accessToken.trim()}`,
            },
        });

        if (response.status === 401) {
             console.error('Сессия истекла или токен недействителен (401).');
             handleLogout();
             return;
        }

        if (response.status === 404) {
             throw new Error('Пользователь не найден.');
        }

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ detail: 'Неизвестная ошибка сервера.' }));
            throw new Error(errorData.detail || `Ошибка сервера: ${response.status}`);
        }

        const user = await response.json();
        renderUserDetails(user);

    }catch (error) {
        let errorMessage = error.message || 'Неизвестная ошибка';
        const detailContent = document.getElementById('user-detail-content');

        if (detailContent) {
            detailContent.innerHTML =
                `<p class="text-red-500 text-center p-8">Ошибка загрузки профиля: ${errorMessage}</p>`;
        }

        setStatus('Ошибка: ' + errorMessage, true);
    }
}


// --- ЛОГИКА МОДАЛЬНОГО ОКНА РЕДАКТИРОВАНИЯ ---

function openEditUserForm(user) {
    const editUserModal = document.getElementById('edit-user-modal');
    const modalContent = document.getElementById('edit-user-modal-content');

    if (!editUserModal || !modalContent) return;

    authUserData = getAuthUserData(); // Обновляем данные на случай изменения ролей
    const isSelf = authUserData.id === user.id;
    const isAdmin = authUserData.role === 'admin';

    const canEditAdminFields = isAdmin;
    const canEditBasicFields = isSelf || isAdmin;

    let formHTML = `
        <form id="edit-user-form" class="space-y-4">
            <h3 class="text-xl font-semibold mb-4">Редактирование профиля: ${user.first_name || user.email}</h3>

            <div class="mb-3">
                <label for="edit-first-name" class="block text-sm font-medium text-gray-700">Имя:</label>
                <input type="text" id="edit-first-name" name="first_name" value="${user.first_name || ''}"
                       class="mt-1 p-2 w-full border rounded-md"
                       ${canEditBasicFields ? '' : 'disabled'}>
            </div>

            <div class="mb-3">
                <label for="edit-last-name" class="block text-sm font-medium text-gray-700">Фамилия:</label>
                <input type="text" id="edit-last-name" name="last_name" value="${user.last_name || ''}"
                       class="mt-1 p-2 w-full border rounded-md"
                       ${canEditBasicFields ? '' : 'disabled'}>
            </div>

            ${canEditAdminFields ? `
                <hr class="my-4">
                <h4 class="font-medium mb-3">Административные настройки</h4>

                <div class="mb-3">
                    <label for="edit-position" class="block text-sm font-medium text-gray-700">Должность:</label>
                    <input type="text" id="edit-position" name="position" value="${user.position || ''}" class="mt-1 p-2 w-full border rounded-md">
                </div>

                <div class="mb-3">
                    <label for="edit-role" class="block text-sm font-medium text-gray-700">Роль:</label>
                    <select id="edit-role" name="role" class="mt-1 p-2 w-full border rounded-md">
                        <option value="admin" ${user.role === 'admin' ? 'selected' : ''}>Администратор</option>
                        <option value="owner" ${user.role === 'owner' ? 'selected' : ''}>Владелец проекта</option>
                        <option value="member" ${user.role === 'member' ? 'selected' : ''}>Участник</option>
                    </select>
                </div>
            ` : ''}
            <button type="submit" class="w-full bg-indigo-600 text-white p-2 rounded-md hover:bg-indigo-700 transition mt-4">Сохранить изменения</button>
        </form>
    `;

    modalContent.innerHTML = formHTML;
    editUserModal.classList.remove('hidden');

    document.getElementById('edit-user-form')?.addEventListener('submit', (e) => handleEditFormSubmit(e, user.id));
}

async function handleEditFormSubmit(event, userIdToUpdate) {
    event.preventDefault();

    const form = event.target;
    const formData = new FormData(form);
    const data = {};

    formData.forEach((value, key) => { data[key] = value; });
    const is_admin = authUserData.role === 'admin';

    const userData = {};
    const adminData = {};
    let adminFieldsChanged = false;

    const basicFields = ['first_name', 'last_name'];
    const adminFields = ['position', 'role'];

    // Заполнение схем
    Object.keys(data).forEach(key => {
        const value = data[key];
        if (value === '' || value === null) return;

        if (basicFields.includes(key)) {
            userData[key] = value;
        } else if (adminFields.includes(key)) {
            adminData[key] = value;
            adminFieldsChanged = true;
        }
    });

    if (Object.keys(userData).length === 0 && Object.keys(adminData).length === 0) {
        alert('Нет данных для обновления.');
        return;
    }

    let userAdminDataToSend = null;
    if (is_admin && adminFieldsChanged) {
        userAdminDataToSend = adminData;
    }

    const requestBody = {
        user: userData,
        user_admin_data: userAdminDataToSend
    };

    try {
        const response = await fetch(`${API_BASE_URL}/users/${userIdToUpdate}`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${ACCESS_TOKEN}`
            },
            body: JSON.stringify(requestBody)
        });

        if (response.ok) {
            alert('Профиль успешно обновлен!');
            document.getElementById('edit-user-modal')?.classList.add('hidden');
            location.reload();
        } else {
            const error = await response.json();
            let errorMessage = 'Не удалось обновить профиль.';
            if (error.detail) {
                // ... (логика парсинга ошибок) ...
                if (typeof error.detail === 'string') {
                    errorMessage = error.detail;
                } else if (Array.isArray(error.detail)) {
                    errorMessage = error.detail.map(err => `${err.loc.join('.')}: ${err.msg}`).join('; ');
                }
            }
            throw new Error(errorMessage);
        }

    } catch (error) {
        console.error('Ошибка обновления:', error);
        alert(`Ошибка: ${error.message}`);
    }
}


// --- ИНИЦИАЛИЗАЦИЯ ---
document.addEventListener('DOMContentLoaded', () => {

    // Привязка обработчиков навигации и выхода
    document.getElementById('back-link')?.addEventListener('click', (e) => {
        e.preventDefault();
        window.location.href = INDEX_PAGE;
    });

    document.getElementById('logout-button')?.addEventListener('click', handleLogout);

    // Закрытие модального окна
    document.getElementById('close-modal-btn')?.addEventListener('click', () => {
        document.getElementById('edit-user-modal')?.classList.add('hidden');
    });
    document.getElementById('edit-user-modal')?.addEventListener('click', (e) => {
        if (e.target.id === 'edit-user-modal') {
            document.getElementById('edit-user-modal')?.classList.add('hidden');
        }
    });

    // Загрузка данных
    fetchUserDetail();
});