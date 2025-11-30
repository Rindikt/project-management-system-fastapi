// js/task_detail.js

// --- ГЛОБАЛЬНОЕ СОСТОЯНИЕ И УТИЛИТЫ ---
let ACCESS_TOKEN = localStorage.getItem('access_token');
const API_BASE_URL = 'http://127.0.0.1:8000';
let currentTaskId = null;
let currentTaskData = null;

// Элементы UI
const taskMainTitle = document.getElementById('task-main-title');
const backToProjectBtn = document.getElementById('back-to-project-btn');
const taskViewCard = document.getElementById('task-view-card');
const taskEditFormCard = document.getElementById('task-edit-form-card');
const editTaskBtn = document.getElementById('edit-task-btn');
const cancelEditTaskBtn = document.getElementById('cancel-edit-task-btn');
const deleteTaskBtn = document.getElementById('delete-task-btn');
const editTaskForm = document.getElementById('edit-task-form');

// Элементы просмотра
const taskStatusView = document.getElementById('task-status-view');
const taskPriorityView = document.getElementById('task-priority-view');
const taskDescriptionView = document.getElementById('task-description-view');
const taskAssignedToView = document.getElementById('task-assigned-to-view');
const taskDueDateView = document.getElementById('task-due-date-view');
const taskCreatedAtView = document.getElementById('task-created-at-view');
const taskAuthorView = document.getElementById('task-author-view');
const taskIdView = document.getElementById('task-id-view');

// Элементы редактирования
const editTaskTitle = document.getElementById('edit-task-title');
const editTaskDescription = document.getElementById('edit-task-description');
const editTaskPriority = document.getElementById('edit-task-priority');
const editTaskStatus = document.getElementById('edit-task-status');
const editTaskDueDate = document.getElementById('edit-task-due-date');


// --- УТИЛИТА: ИЗВЛЕЧЕНИЕ ID ЗАДАЧИ ИЗ URL ---
function getTaskIdFromUrl() {
    const urlParams = new URLSearchParams(window.location.search);
    const id = urlParams.get('id');
    if (!id) {
        setStatus('Ошибка: ID задачи не найден в URL.', true);
        return null;
    }
    return parseInt(id);
}

// --- ФУНКЦИЯ ОТОБРАЖЕНИЯ ДЕТАЛЕЙ ЗАДАЧИ ---
function renderTaskDetails(task) {
    currentTaskData = task;
    document.getElementById('task-page-title').textContent = task.title;

    // Подготовка данных для отображения
    const priorityText = task.priority.charAt(0).toUpperCase() + task.priority.slice(1);
    const statusText = task.status.replace('_', ' ').charAt(0).toUpperCase() + task.status.replace('_', ' ').slice(1);
    const assignedToName = task.assigned_to ?
        `${task.assigned_to.first_name || 'Неизвестный'} (${task.assigned_to.email})` : 'Не назначен';
    const authorName = task.author ?
        `${task.author.first_name || 'Неизвестный'} (${task.author.email})` : 'Неизвестен';
    const dueDateDisplay = task.due_date ? new Date(task.due_date).toLocaleDateString('ru-RU') : 'Не указан';
    const createdAtDisplay = new Date(task.created_at).toLocaleDateString('ru-RU', { hour: '2-digit', minute: '2-digit' });
    const dateInputFormat = task.due_date ? new Date(task.due_date).toISOString().split('T')[0] : '';

    // Обновление режима просмотра
    taskMainTitle.textContent = task.title;
    taskStatusView.textContent = statusText;
    taskPriorityView.textContent = priorityText;
    taskDescriptionView.textContent = task.description;
    taskAssignedToView.textContent = assignedToName;
    taskDueDateView.textContent = dueDateDisplay;
    taskCreatedAtView.textContent = createdAtDisplay;
    taskAuthorView.textContent = authorName;
    taskIdView.textContent = task.id;

    // Обновление режима редактирования
    editTaskTitle.value = task.title;
    editTaskDescription.value = task.description;
    editTaskPriority.value = task.priority;
    editTaskStatus.value = task.status;
    editTaskDueDate.value = dateInputFormat;

    setStatus(`Задача "${task.title}" успешно загружена.`, false);
}

// --- ФУНКЦИЯ ЗАГРУЗКИ КОНКРЕТНОЙ ЗАДАЧИ ---
async function fetchTaskDetail() {
    if (!ACCESS_TOKEN) {
        window.location.href = 'index.html';
        return;
    }

    currentTaskId = getTaskIdFromUrl();
    if (currentTaskId === null) return;

    try {
        const response = await fetch(`${API_BASE_URL}/tasks/${currentTaskId}`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${ACCESS_TOKEN}`,
            },
        });

        if (response.status === 404) {
             throw new Error('Задача не найдена.');
        }

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ detail: 'Неизвестная ошибка сервера.' }));
            throw new Error(errorData.detail || 'Не удалось загрузить детали задачи.');
        }

        const task = await response.json();
        renderTaskDetails(task);

    } catch (error) {
        document.getElementById('task-detail-content').innerHTML = `<p class="text-red-500 text-center p-8">Ошибка загрузки задачи: ${error.message}</p>`;
        setStatus('Ошибка: ' + error.message, true);
    }
}

// --- УТИЛИТА: ПЕРЕКЛЮЧЕНИЕ РЕЖИМА РЕДАКТИРОВАНИЯ ---
function toggleEditMode(isEditing) {
    if (isEditing) {
        taskViewCard.classList.add('hidden');
        taskEditFormCard.classList.remove('hidden');
    } else {
        taskViewCard.classList.remove('hidden');
        taskEditFormCard.classList.add('hidden');
    }
}

// --- ОБРАБОТЧИКИ СОБЫТИЙ И ИНИЦИАЛИЗАЦИЯ ---
document.addEventListener('DOMContentLoaded', () => {
    fetchTaskDetail();

    // Навигация
    backToProjectBtn.addEventListener('click', () => {
        // Мы предполагаем, что у вас есть task.project_id в данных задачи
        if (currentTaskData && currentTaskData.project_id) {
            window.location.href = `project_detail.html?id=${currentTaskData.project_id}`;
        } else {
             window.location.href = 'index.html'; // Fallback
        }
    });

    // Редактирование
    editTaskBtn.addEventListener('click', () => toggleEditMode(true));
    cancelEditTaskBtn.addEventListener('click', () => toggleEditMode(false));
    editTaskForm.addEventListener('submit', handleEditTask); // Предполагается, что handleEditTask будет в api_handlers.js
    deleteTaskBtn.addEventListener('click', handleDeleteTask); // Предполагается, что handleDeleteTask будет в api_handlers.js
});