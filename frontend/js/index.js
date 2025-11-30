// --- ГЛОБАЛЬНОЕ СОСТОЯНИЕ И УТИЛИТЫ ---
let ACCESS_TOKEN = localStorage.getItem('access_token');
// Используем относительный путь для перехода к project_detail.html
const PROJECT_DETAIL_PAGE = 'project_detail.html';
const USER_PROFILE_PAGE = 'user_detail.html'; // <<< ДОБАВЛЕНО: Страница профиля
const API_BASE_URL = 'http://127.0.0.1:8000';

const statusMessage = document.getElementById('status-message');
const authSection = document.getElementById('auth-section');
const appSection = document.getElementById('app-section');
const currentTokenDisplay = document.getElementById('current-token');
const logoutButton = document.getElementById('logout-button');
const projectsListContainer = document.getElementById('projects-list');

// Элемент ссылки на профиль (id="link-my-profile" из index.html)
const profileLink = document.getElementById('link-my-profile'); // <<< ДОБАВЛЕНО

// Элементы для модального окна
const createProjectBtn = document.getElementById('create-project-btn');
const projectModal = document.getElementById('project-modal');
const closeModalBtn = document.getElementById('close-modal-btn');
const createProjectForm = document.getElementById('create-project-form');
// Элементы переключения вкладок
const tabLogin = document.getElementById('tab-login');
const tabRegister = document.getElementById('tab-register');
const loginTabContent = document.getElementById('login-tab');
const registerTabContent = document.getElementById('register-tab');


// --- УТИЛИТА: Получение ID авторизованного пользователя ---
function getAuthUserId() {
    try {
        const userDataString = localStorage.getItem('auth_user_data');
        if (userDataString) {
            const data = JSON.parse(userDataString);
            return data.id; // Возвращаем сохраненный ID
        }
    } catch (e) {
        console.error("Ошибка при чтении auth_user_data:", e);
    }
    return null;
}

function setStatus(message, isError = false) {
    statusMessage.textContent = message;
    if (isError) {
        statusMessage.className = 'mt-2 p-2 rounded-lg text-sm text-red-700 bg-red-100 transition-all duration-300 min-h-6';
    } else {
        statusMessage.className = 'mt-2 p-2 rounded-lg text-sm text-green-700 bg-green-100 transition-all duration-300 min-h-6';
    }
    // Очистка сообщения через 5 секунд
    setTimeout(() => {
        statusMessage.textContent = '';
        statusMessage.className = 'mt-2 p-2 rounded-lg text-sm transition-all duration-300 min-h-6';
    }, 5000);
}

function showModal() {
    projectModal.classList.remove('hidden');
    projectModal.classList.add('flex');
}

function hideModal() {
    projectModal.classList.add('hidden');
    projectModal.classList.remove('flex');
    createProjectForm.reset(); // Очистить форму при закрытии
}

// --- ФУНКЦИЯ ПЕРЕХОДА НА СТРАНИЦУ ПРОФИЛЯ ---
function navigateToProfile() { // <<< НОВАЯ ФУНКЦИЯ
    const userId = getAuthUserId();
    if (userId) {
        // Перенаправляем на user_detail.html, передавая ID пользователя как параметр URL
        window.location.href = `${USER_PROFILE_PAGE}?id=${userId}`;
    } else {
        setStatus('Ошибка: Не удалось найти ID авторизованного пользователя.', true);
        handleLogout();
    }
}


// --- ФУНКЦИЯ ПЕРЕХОДА НА СТРАНИЦУ ДЕТАЛЕЙ ПРОЕКТА ---
function navigateToProjectDetail(projectId) {
    // Перенаправляем на project_detail.html, передавая ID проекта как параметр URL
    window.location.href = `${PROJECT_DETAIL_PAGE}?id=${projectId}`;
}


// --- ФУНКЦИЯ ОТОБРАЖЕНИЯ ПРОЕКТОВ ---
function renderProjects(projects) {
    projectsListContainer.innerHTML = ''; // Очистка

    if (projects.length === 0) {
        projectsListContainer.innerHTML = '<p class="text-gray-500 text-center p-4 border-2 border-dashed border-gray-200 rounded-lg">У вас пока нет проектов. Создайте первый!</p>';
        return;
    }

    projects.forEach(project => {
        const title = project.title || 'Без названия';
        const description = project.description || 'Описание отсутствует.';
        const dueDate = project.dub_date ? new Date(project.dub_date).toLocaleDateString('ru-RU') : 'Не указан';

        let ownerName = 'Неизвестен';
        if (project.owner && project.owner.first_name) {
            ownerName = `${project.owner.first_name}`;
            if (project.owner.last_name) {
                 ownerName += ` ${project.owner.last_name.charAt(0)}.`
            }
        }


        const projectCard = document.createElement('div');
        projectCard.setAttribute('data-project-id', project.id);
        // Добавляем обработчик клика для перехода на страницу деталей
        projectCard.addEventListener('click', () => navigateToProjectDetail(project.id));

        projectCard.className = 'bg-gray-50 p-4 rounded-lg shadow-sm border border-gray-200 hover:shadow-md hover:border-indigo-300 transition-all cursor-pointer';
        projectCard.innerHTML = `
            <div class="flex justify-between items-start">
                <h3 class="text-lg font-semibold text-indigo-700">${title}</h3>
                <span class="text-xs font-mono bg-indigo-100 text-indigo-600 px-2 py-1 rounded-full">${project.id}</span>
            </div>
            <p class="text-gray-600 mt-2 text-sm line-clamp-2">${description}</p>
            <div class="flex justify-between items-center mt-3 pt-3 border-t border-gray-200 text-xs text-gray-500">
                <span>Срок: ${dueDate}</span>
                <span>Владелец: ${ownerName}</span>
            </div>
        `;
        projectsListContainer.appendChild(projectCard);
    });
}

// --- ФУНКЦИЯ ЗАГРУЗКИ ПРОЕКТОВ ---
async function fetchProjects() {
    projectsListContainer.innerHTML = '<p class="text-gray-400 text-center p-4">Загрузка проектов...</p>';

    try {
        const response = await fetch(`${API_BASE_URL}/projects/`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${ACCESS_TOKEN}`,
                'Content-Type': 'application/json',
            },
        });

        if (response.status === 401) {
            handleLogout();
            setStatus('Сессия истекла. Пожалуйста, войдите снова.', true);
            return;
        }

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ detail: 'Неизвестная ошибка сервера.' }));
            throw new Error(errorData.detail || 'Не удалось загрузить список проектов.');
        }

        const projects = await response.json();
        renderProjects(projects);
        setStatus('Проекты успешно загружены.', false);

    } catch (error) {
        projectsListContainer.innerHTML = `<p class="text-red-500 text-center p-4">Ошибка загрузки: ${error.message}</p>`;
        setStatus('Ошибка при загрузке проектов: ' + error.message, true);
    }
}

function renderApp() {
    if (ACCESS_TOKEN) {
        authSection.classList.add('hidden');
        appSection.classList.remove('hidden');
        currentTokenDisplay.textContent = ACCESS_TOKEN;
        fetchProjects();
    } else {
        authSection.classList.remove('hidden');
        appSection.classList.add('hidden');
        currentTokenDisplay.textContent = 'Отсутствует';
        // Убедимся, что при выходе всегда активна вкладка "Вход"
        setActiveTab('login');
    }
}

// --- ФУНКЦИЯ СОЗДАНИЯ ПРОЕКТА ---
async function handleCreateProject(e) {
    e.preventDefault();
    const title = document.getElementById('project-name').value.trim();
    const description = document.getElementById('project-description').value.trim();
    const dueDate = document.getElementById('project-due-date').value.trim();

    const newProject = {
        title: title,
        description: description || null,
        dub_date: dueDate || null
    };

    try {
        const response = await fetch(`${API_BASE_URL}/projects/`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${ACCESS_TOKEN}`,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(newProject)
        });

        if (!response.ok) {
            let errorDetail = 'Неизвестная ошибка создания проекта.';
            try {
                const errorData = await response.json();
                if (Array.isArray(errorData.detail)) {
                    errorDetail = `Ошибка валидации: ${errorData.detail[0].msg} (поле: ${errorData.detail[0].loc.slice(-1)})`;
                } else {
                    errorDetail = errorData.detail || 'Ошибка сервера.';
                }
            } catch (e) {
                errorDetail = `Сервер вернул ошибку ${response.status} без деталей.`;
            }

            throw new Error(errorDetail);
        }

        hideModal();
        const createdProject = await response.json();
        setStatus(`Проект "${createdProject.title}" успешно создан!`, false);
        // Перезагружаем список проектов
        fetchProjects();

    } catch (error) {
        setStatus('Ошибка создания проекта: ' + error.message, true);
    }
}

// --- ФУНКЦИИ АУТЕНТИФИКАЦИИ ---

function setActiveTab(tabName) {
    // Убираем активные стили со всех
    tabLogin.classList.remove('border-indigo-500', 'text-indigo-600');
    tabLogin.classList.add('border-transparent', 'text-gray-500', 'hover:border-gray-300');
    tabRegister.classList.remove('border-indigo-500', 'text-indigo-600');
    tabRegister.classList.add('border-transparent', 'text-gray-500', 'hover:border-gray-300');

    // Скрываем все контенты
    loginTabContent.classList.add('hidden');
    registerTabContent.classList.add('hidden');

    // Устанавливаем активную вкладку
    if (tabName === 'login') {
        tabLogin.classList.add('border-indigo-500', 'text-indigo-600');
        tabLogin.classList.remove('border-transparent', 'text-gray-500', 'hover:border-gray-300');
        loginTabContent.classList.remove('hidden');
    } else if (tabName === 'register') { // Добавлено явное условие для 'register'
        tabRegister.classList.add('border-indigo-500', 'text-indigo-600');
        tabRegister.classList.remove('border-transparent', 'text-gray-500', 'hover:border-gray-300');
        registerTabContent.classList.remove('hidden');
    }
}

// ИСПРАВЛЕННАЯ ФУНКЦИЯ: Получение профиля текущего пользователя
async function fetchCurrentUserProfile() {
    if (!ACCESS_TOKEN || ACCESS_TOKEN.trim() === '') {
        handleLogout();
        throw new Error('Токен доступа отсутствует или некорректен.');
    }
    const trimmedToken = ACCESS_TOKEN.trim();

    const response = await fetch(`${API_BASE_URL}/users/me`, {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${trimmedToken}`,
        },
    });

    if (response.status === 401) {
        throw new Error('Сессия истекла или токен недействителен (401). Пожалуйста, войдите снова.');
    }

    if (!response.ok) {
        // Мы используем response.json() здесь, чтобы получить детали ошибки 422
        // Но если 422 возвращает невалидный JSON, catch поймает это.
        let errorDetail = 'Ошибка сервера при запросе профиля.';
        try {
            const errorData = await response.json();

            // Если мы получаем ошибку валидации 422, выводим её в явном виде
            if (response.status === 422 && Array.isArray(errorData.detail)) {
                 errorDetail = `Ошибка валидации (422): ${errorData.detail[0].msg} (поле: ${errorData.detail[0].loc.slice(-1)})`;
            } else {
                 errorDetail = errorData.detail || `Ошибка сервера: ${response.status}`;
            }

        } catch (e) {
            errorDetail = `Ошибка ${response.status}. Сервер вернул нечитаемый ответ.`;
        }
        throw new Error(errorDetail);
    }

    return await response.json();
}

// ИСПРАВЛЕННАЯ ФУНКЦИЯ: handleLogin (ВОССТАНОВЛЕНО)
async function handleLogin(e) {
    e.preventDefault();

    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;

    try {
        const formBody = new URLSearchParams();
        formBody.append('username', email);
        formBody.append('password', password);

        // 1. ПОЛУЧЕНИЕ ТОКЕНА
        const tokenResponse = await fetch(`${API_BASE_URL}/users/token`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: formBody.toString()
        });

        if (!tokenResponse.ok) {
            const errorData = await tokenResponse.json().catch(() => ({ detail: 'Неизвестная ошибка сервера.' }));
            throw new Error(errorData.detail || 'Ошибка входа. Проверьте email и пароль.');
        }

        const data = await tokenResponse.json();

        ACCESS_TOKEN = data.access_token;
        localStorage.setItem('access_token', ACCESS_TOKEN);
// !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        // 2. ПОЛУЧЕНИЕ ДАННЫХ ПОЛЬЗОВАТЕЛЯ (/users/me)
        const userProfile = await fetchCurrentUserProfile();

        // 3. СОХРАНЕНИЕ ID И РОЛИ В localStorage (Чистый рабочий вариант)
        const authDataToSave = {
            id: userProfile.id, // Используем ID как есть, без принудительного парсинга
            role: userProfile.role
        };
        localStorage.setItem('auth_user_data', JSON.stringify(authDataToSave));

        setStatus('Успешный вход! Данные профиля сохранены.', false);
        renderApp();

    } catch (error) {
        handleLogout();
        // ГАРАНТИРОВАННЫЙ ВЫВОД СООБЩЕНИЯ
        const errorMessage = error.message || String(error);
        setStatus('Ошибка входа: ' + errorMessage, true);
    }
}

async function handleRegister(e) {
    e.preventDefault();
    const user = {
        first_name: document.getElementById('reg-first-name').value,
        last_name: document.getElementById('reg-last-name').value,
        email: document.getElementById('reg-email').value,
        position: document.getElementById('reg-position').value || null,
        password: document.getElementById('reg-password').value
    };

    try {
        const response = await fetch(`${API_BASE_URL}/users/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(user)
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ detail: 'Неизвестная ошибка сервера.' }));
            let errorMsg = errorData.detail || 'Ошибка регистрации.';
            if (Array.isArray(errorData.detail)) {
                errorMsg = `Ошибка валидации: ${errorData.detail[0].msg} (поле: ${errorData.detail[0].loc.slice(-1)})`;
            }
            throw new Error(errorMsg);
        }

        setStatus('Регистрация прошла успешно! Теперь войдите.', false);
        setActiveTab('login'); // Переключаемся на вкладку входа после успешной регистрации

    } catch (error) {
        setStatus('Ошибка регистрации: ' + error.message, true);
    }
}

function handleLogout() {
    ACCESS_TOKEN = null;
    localStorage.removeItem('access_token');
    localStorage.removeItem('auth_user_data');
    setStatus('Вы успешно вышли из системы.', false);
    renderApp();
}

// --- ОБРАБОТЧИКИ СОБЫТИЙ ---
// Убедитесь, что все элементы найдены
if (document.getElementById('login-form')) {
    document.getElementById('login-form').addEventListener('submit', handleLogin);
}
if (document.getElementById('register-form')) {
    document.getElementById('register-form').addEventListener('submit', handleRegister);
}
if (logoutButton) {
    logoutButton.addEventListener('click', handleLogout);
}

// Обработчики для модального окна создания проекта
if (createProjectBtn) {
    createProjectBtn.addEventListener('click', showModal);
}
if (closeModalBtn) {
    closeModalBtn.addEventListener('click', hideModal);
}
if (createProjectForm) {
    createProjectForm.addEventListener('submit', handleCreateProject);
}
// Закрытие модального окна по клику вне формы
if (projectModal) {
    projectModal.addEventListener('click', (e) => {
        if (e.target === projectModal) {
            hideModal();
        }
    });
}

// Обработчики переключения вкладок
if (tabLogin) {
    tabLogin.addEventListener('click', () => setActiveTab('login'));
}
if (tabRegister) {
    tabRegister.addEventListener('click', () => setActiveTab('register'));
}

// Обработчик для ссылки "Мой Профиль"
if (profileLink) { // <<< ДОБАВЛЕНО
    profileLink.addEventListener('click', (e) => {
        e.preventDefault(); // Предотвращаем переход по '#'
        navigateToProfile();
    });
}


// Инициализация при загрузке страницы
renderApp();