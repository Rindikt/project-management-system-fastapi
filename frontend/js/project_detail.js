// --- ГЛОБАЛЬНОЕ СОСТОЯНИЕ И УТИЛИТЫ ---
let ACCESS_TOKEN = localStorage.getItem('access_token');
const API_BASE_URL = 'http://127.0.0.1:8000';
let currentProjectId = null;
let currentProjectData = null;
let currentProjectMembers = [];

// Элементы UI
// const statusMessage - определён в rendering.js
const projectDetailContent = document.getElementById('project-detail-content');
const projectMainTitle = document.getElementById('project-main-title');

// ИСПРАВЛЕНИЕ 1: taskCountSpan в HTML имеет ID 'task-count', но мы его не использовали в rendering.js.
// Чтобы избежать конфликта с кодом, который я ранее предоставлял,
// либо используйте 'task-count' в rendering.js, либо используйте 'task-count-span' в HTML.
// Если вы используете 'task-count' в HTML, тогда:
const taskCountSpan = document.getElementById('task-count');
// Если в rendering.js у вас была переменная taskCountSpan,
// но она не была объявлена в rendering.js, это вызывало ошибку.
// Учитывая, что в rendering.js вы использовали taskCountSpan:
// Вам нужно добавить эту строку в rendering.js (как объявление),
// а здесь она уже есть. Проблема не здесь.
// ОСТАВЛЯЕМ КАК ЕСТЬ.

// Элементы задач
const createTaskForm = document.getElementById('create-task-form');
const taskTitleInput = document.getElementById('task-title');
const taskDescriptionInput = document.getElementById('task-description');
const taskPrioritySelect = document.getElementById('task-priority');

// ИСПРАВЛЕНИЕ 2: Для согласованности с rendering.js (где часто используется select)
// ОСТАВЛЯЕМ КАК ЕСТЬ: taskAssignedToSelect = document.getElementById('task-assigned-to-email')

const taskAssignedToSelect = document.getElementById('task-assigned-to-email');
const projectTasksList = document.getElementById('project-tasks-list');
const tasksPlaceholder = document.getElementById('tasks-placeholder');


// Остальные элементы UI
const backToListBtn = document.getElementById('back-to-list-btn');
const projectViewCard = document.getElementById('project-view-card');
const editProjectBtn = document.getElementById('edit-project-btn');
const projectDescriptionView = document.getElementById('project-description-view');
const projectOwnerView = document.getElementById('project-owner-view');
const projectDueDateView = document.getElementById('project-due-date-view');
const projectIdView = document.getElementById('project-id-view'); // <-- ЭТО ИМЯ СООТВЕТСТВУЕТ HTML
const deleteProjectBtn = document.getElementById('delete-project-btn');
const projectEditFormCard = document.getElementById('project-edit-form-card');
const editProjectForm = document.getElementById('edit-project-form');
const cancelEditBtn = document.getElementById('cancel-edit-btn');
const editProjectName = document.getElementById('edit-project-name');
const editProjectDescription = document.getElementById('edit-project-description');
const editProjectDueDate = document.getElementById('edit-project-due-date');
const projectMembersList = document.getElementById('project-members-list');
const membersPlaceholder = document.getElementById('members-placeholder');
const addMemberForm = document.getElementById('add-member-form');

const taskDueDateInput = document.getElementById('task-due-date');


// --- УТИЛИТА: ИЗВЛЕЧЕНИЕ ID ПРОЕКТА ИЗ URL ---
function getProjectIdFromUrl() {
    const urlParams = new URLSearchParams(window.location.search);
    const id = urlParams.get('id');
    if (!id) {
        setStatus('Ошибка: ID проекта не найден в URL.', true);
        return null;
    }
    return parseInt(id);
}

// Вспомогательная функция для переключения режима редактирования
function toggleEditMode(isEditing) {
    if (isEditing) {
        projectViewCard.classList.add('hidden');
        projectEditFormCard.classList.remove('hidden');
    } else {
        projectViewCard.classList.remove('hidden');
        projectEditFormCard.classList.add('hidden');
    }
}

// --- ФУНКЦИЯ ОТОБРАЖЕНИЯ ДЕТАЛЕЙ ПРОЕКТА ---
function renderProjectDetails(project) {
    // Обновление глобального состояния
    currentProjectData = project;
    currentProjectMembers = Array.isArray(project.members) ? project.members : [];

    // Подготовка данных
    const title = project.title || 'Без названия';
    const description = project.description || 'Описание отсутствует.';

    // ИСПРАВЛЕНИЕ: Используем 'dub_date'
    const dueDate = project.dub_date ? new Date(project.dub_date).toLocaleDateString('ru-RU') : 'Не указан';

    // ИСПРАВЛЕНИЕ: Формат для поля input[type="date"]
    const dateInputFormat = project.dub_date ? new Date(project.dub_date).toISOString().split('T')[0] : '';

    let ownerName = 'Неизвестен';
    if (project.owner) {
        if (project.owner.first_name) {
            ownerName = `${project.owner.first_name}`;
            if (project.owner.last_name) {
                 ownerName += ` ${project.owner.last_name.charAt(0)}.`
            }
        } else if (project.owner.email) {
             ownerName = project.owner.email;
        }
    }

    // --- ОБНОВЛЕНИЕ РЕЖИМА ПРОСМОТРА (VIEW) ---
    // ИСПРАВЛЕНИЕ: Используем projectMainTitle
    projectMainTitle.textContent = title;

    projectDescriptionView.textContent = description;
    projectOwnerView.textContent = ownerName;
    projectDueDateView.textContent = dueDate;
    projectIdView.textContent = project.id;

    // --- ОБНОВЛЕНИЕ РЕЖИМА РЕДАКТИРОВАНИЯ (EDIT) ---
    editProjectName.value = title;
    editProjectDescription.value = description;
    editProjectDueDate.value = dateInputFormat;

    // --- ВЫЗОВ РЕНДЕРИНГА СВЯЗАННЫХ СУЩНОСТЕЙ (из rendering.js) ---
    renderMembers(currentProjectMembers, project.owner);
    populateAssignedToSelect(currentProjectMembers, project.owner);
    renderTasks(project.tasks);

    // Установка финального статуса
    setStatus(`Проект "${title}" успешно загружен.`, false);
}
// --- ФУНКЦИЯ ЗАГРУЗКИ КОНКРЕТНОГО ПРОЕКТА ---
async function fetchProjectDetail() {
    if (!ACCESS_TOKEN) {
        window.location.href = 'index.html';
        return;
    }

    currentProjectId = getProjectIdFromUrl();
    if (currentProjectId === null) return;

    projectDetailContent.classList.add('opacity-50', 'pointer-events-none');

    try {
        const response = await fetch(`${API_BASE_URL}/projects/${currentProjectId}`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${ACCESS_TOKEN}`,
                'Content-Type': 'application/json',
            },
        });

        if (response.status === 401) {
            setStatus('Сессия истекла. Перенаправление на страницу входа.', true);
            setTimeout(() => window.location.href = 'index.html', 2000);
            return;
        }

        if (response.status === 404) {
             throw new Error('Проект не найден.');
        }

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ detail: 'Неизвестная ошибка сервера.' }));
            throw new Error(errorData.detail || 'Не удалось загрузить детали проекта.');
        }

        const project = await response.json();
        renderProjectDetails(project);

    } catch (error) {
        projectDetailContent.innerHTML = `<p class="text-red-500 text-center p-8">Ошибка загрузки проекта: ${error.message}</p>`;
        setStatus('Ошибка: ' + error.message, true);
    } finally {
        projectDetailContent.classList.remove('opacity-50', 'pointer-events-none');
    }
}


// --- ОБРАБОТЧИКИ СОБЫТИЙ И ИНИЦИАЛИЗАЦИЯ ---

document.addEventListener('DOMContentLoaded', () => {
    // Запуск загрузки данных при загрузке страницы
    fetchProjectDetail();

    // Навигация
    backToListBtn.addEventListener('click', () => {
        window.location.href = 'index.html';
    });

    // Редактирование проекта (логика в api_handlers.js)
    editProjectBtn.addEventListener('click', () => toggleEditMode(true));
    cancelEditBtn.addEventListener('click', () => toggleEditMode(false));
    editProjectForm.addEventListener('submit', handleEditProject);
    deleteProjectBtn.addEventListener('click', handleDeleteProject);

    // Добавление участника (логика в api_handlers.js)
    addMemberForm.addEventListener('submit', handleAddMember);

    // Создание задачи (логика в api_handlers.js)
    createTaskForm.addEventListener('submit', handleCreateTask);
});