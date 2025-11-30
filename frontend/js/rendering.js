// --- УТИЛИТА: Установка статуса ---
const statusMessage = document.getElementById('status-message');

function setStatus(message, isError = false) {
    // Установка класса для сообщения
    const baseClass = 'mt-2 p-2 rounded-lg text-sm transition-all duration-300 min-h-6';
    statusMessage.textContent = message;
    if (isError) {
        statusMessage.className = `${baseClass} text-red-700 bg-red-100`;
    } else {
        statusMessage.className = `${baseClass} text-green-700 bg-green-100`;
    }

    // Очистка сообщения через 5 секунд
    setTimeout(() => {
        statusMessage.textContent = '';
        statusMessage.className = baseClass;
    }, 5000);
}

// Вспомогательные функции для отображения приоритета
function getPriorityStyles(priority) {
    switch (priority) {
        case 'high':
            return 'bg-red-100 text-red-600 font-medium';
        case 'medium':
            return 'bg-yellow-100 text-yellow-600 font-medium';
        case 'low':
            return 'bg-green-100 text-green-600';
        default:
            return 'bg-gray-100 text-gray-600';
    }
}

function getPriorityDisplay(priority) {
    switch (priority) {
        case 'high':
            return 'Высокий';
        case 'medium':
            return 'Средний';
        case 'low':
            return 'Низкий';
        default:
            return 'Не указан';
    }
}

// --- ФУНКЦИЯ ЗАПОЛНЕНИЯ ВЫБОР ИСПОЛНИТЕЛЯ ---
function populateAssignedToSelect(members, owner) {
    taskAssignedToSelect.innerHTML = ''; // Очистка

    // 1. Добавляем опцию по умолчанию "Не назначен"
    const defaultOption = document.createElement('option');
    defaultOption.value = '';
    defaultOption.textContent = '— Не назначен —';
    taskAssignedToSelect.appendChild(defaultOption);

    // Определяем ID владельца для исключения дублирования
    const ownerId = owner ? owner.id : null;

    // Создаем карту пользователей, используя ID как ключ для исключения дублирования
    const allUsers = {};
    if (owner) {
        allUsers[owner.id] = {...owner, is_owner: true};
    }

    (members || []).forEach(member => {
        // Убеждаемся, что мы не перезаписываем владельца, если он пришел в members
        if (!allUsers[member.id]) {
            allUsers[member.id] = member;
        }
    });

    const sortedUsers = Object.values(allUsers).sort((a, b) => {
        const nameA = a.first_name || a.email; // Теперь email должен быть
        const nameB = b.first_name || b.email; // Теперь email должен быть
        return nameA.localeCompare(nameB, 'ru', { sensitivity: 'base' });
    });

    // 2. Добавляем всех участников
    sortedUsers.forEach(member => {
        const option = document.createElement('option');
        option.value = member.email; // Используем email, который теперь есть!

        let displayName = member.first_name || '';
        if (member.last_name) {
            displayName += ` ${member.last_name.charAt(0)}.`
        }

        if (!displayName.trim()) {
            displayName = member.email;
        }

        const isOwner = member.is_owner || (ownerId === member.id);
        option.textContent = displayName.trim() + (isOwner ? ' (Владелец)' : '');

        taskAssignedToSelect.appendChild(option);
    });
}
// --- ФУНКЦИЯ РЕНДЕРИНГА УЧАСТНИКОВ (С КЛИКАБЕЛЬНЫМИ ССЫЛКАМИ НА user_detail.html) ---
function renderMembers(members, owner) {
    projectMembersList.innerHTML = '';

    // 1. Объединяем владельца и участников в один словарь по ID для исключения дубликатов
    const allUsers = {};
    const ownerId = owner ? owner.id : null;

    if (owner) {
        allUsers[owner.id] = { ...owner, is_owner: true };
    }

    (members || []).forEach(member => {
        if (!allUsers[member.id]) {
            allUsers[member.id] = member;
        }
    });

    const sortedUsers = Object.values(allUsers).sort((a, b) => {
        const nameA = a.first_name || a.email;
        const nameB = b.first_name || b.email;
        return nameA.localeCompare(nameB, 'ru', { sensitivity: 'base' });
    });

    if (sortedUsers.length === 0) {
        membersPlaceholder.classList.remove('hidden');
        membersPlaceholder.textContent = 'Участники не загружены.';
        return;
    }
    membersPlaceholder.classList.add('hidden');

    // 2. Отрисовка
    sortedUsers.forEach(member => {
        const memberDiv = document.createElement('div');
        // memberDiv больше не будет иметь основной стиль, так как его примет тег <a>
        memberDiv.className = 'p-0';

        // Убираем data-user-id с внешнего div, он не нужен

        let fullName = member.first_name || '';
        if (member.last_name) {
            // Форматирование: Имя Фамилия.
            fullName += ` ${member.last_name.charAt(0)}.`;
        }

        const primaryDisplay = fullName.trim() || member.email;
        const secondaryDisplay = fullName.trim() ? member.email : '';

        const isOwner = member.is_owner || (ownerId === member.id);

        // !!! ИЗМЕНЕНИЕ 1: Оборачиваем в тег <a> для перехода на user_detail.html
        memberDiv.innerHTML = `
            <a href="user_detail.html?id=${member.id}"
               class="flex justify-between items-center p-2 bg-gray-50 rounded-lg border hover:bg-gray-100 transition-colors cursor-pointer block">
                <div class="flex flex-col truncate w-3/4">
                    <span class="text-sm font-medium text-gray-700 truncate">
                        ${primaryDisplay}
                        ${isOwner ? '<span class="text-indigo-600 font-normal">(Владелец)</span>' : ''}
                    </span>
                    ${secondaryDisplay && !isOwner ? `<span class="text-xs text-gray-500 truncate">${secondaryDisplay}</span>` : ''}
                </div>
                ${!isOwner ? `
                    <button type="button" data-user-id="${member.id}"
                            class="remove-member-btn text-red-400 hover:text-red-600 p-1 rounded transition-colors"
                            title="Удалить участника"
                            onclick="event.stopPropagation();">
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="w-5 h-5">
                            <path fill-rule="evenodd" d="M16.5 4.475C17.757 4.475 19.167 4.885 20.372 5.517A7.5 7.5 0 0 1 21.75 12a7.5 7.5 0 0 1-1.378 6.483c-1.205.632-2.615 1.042-3.872 1.042h-9c-1.257 0-2.667-.41-3.872-1.042A7.5 7.5 0 0 1 2.25 12a7.5 7.5 0 0 1 1.378-6.483C4.811 4.885 6.221 4.475 7.5 4.475h9zM8.583 8.583a.75.75 0 0 0 1.06 1.06L12 10.94l2.357-2.357a.75.75 0 0 0 1.06 1.06L13.06 12l2.357 2.357a.75.75 0 1 0-1.06 1.06L12 13.06l-2.357 2.357a.75.75 0 1 0-1.06-1.06L10.94 12l-2.357-2.357z" clip-rule="evenodd" />
                        </svg>
                    </button>
                ` : ''}
            </a>
        `;

        projectMembersList.appendChild(memberDiv);
    });

    // 3. Обработчик клика (Удаление)
    // !!! ИЗМЕНЕНИЕ 2: Используем event.stopPropagation() выше,
    // чтобы предотвратить переход по ссылке.
    projectMembersList.querySelectorAll('.remove-member-btn').forEach(button => {
        button.addEventListener('click', (e) => handleRemoveMember(e.currentTarget.dataset.userId));
    });
}
// --- ФУНКЦИЯ РЕНДЕРИНГА ЗАДАЧ (ОБНОВЛЕННАЯ С КЛИКАБЕЛЬНОЙ ССЫЛКОЙ) ---
function renderTasks(tasks) {
    projectTasksList.innerHTML = '';
    taskCountSpan.textContent = tasks ? tasks.length : 0;

    if (!tasks || tasks.length === 0) {
        tasksPlaceholder.classList.remove('hidden');
        return;
    }
    tasksPlaceholder.classList.add('hidden');

    tasks.forEach(task => {
        // Создаем контейнер для задачи
        const taskDiv = document.createElement('div');
        taskDiv.className = 'p-3 bg-white border border-gray-200 rounded-lg shadow-sm hover:shadow-md transition-shadow';

        const created = task.created_at ? new Date(task.created_at).toLocaleDateString('ru-RU') : 'N/A';

        let assignedUserHtml = '<span class="text-gray-400">Не назначен</span>';
        if (task.assigned_to) {
            let assignedName = task.assigned_to.first_name || '';
            if (task.assigned_to.last_name) {
                assignedName += ` ${task.assigned_to.last_name.charAt(0)}.`
            }
            const displayText = assignedName.trim() || task.assigned_to.email;
            assignedUserHtml = `<span class="font-medium text-gray-700">${displayText}</span>`;
        }

        const dueDateDisplay = task.due_date ? new Date(task.due_date).toLocaleDateString('ru-RU') : 'Нет';

        // --- КЛИКАБЕЛЬНАЯ ССЫЛКА ---
        taskDiv.innerHTML = `
            <a href="task_detail.html?id=${task.id}" class="block transition-colors cursor-pointer">
                <div class="flex justify-between items-start">
                    <h4 class="text-base font-semibold text-gray-800">${task.title}</h4>
                    <div class="flex items-center space-x-2 flex-shrink-0">
                        <span class="text-xs px-2 py-0.5 rounded ${getPriorityStyles(task.priority)}">${getPriorityDisplay(task.priority)}</span>
                        <span class="text-xs px-2 py-0.5 bg-gray-200 text-gray-600 rounded">${task.status || 'todo'}</span>
                    </div>
                </div>
                <p class="text-sm text-gray-600 mt-1">${task.description || 'Нет описания.'}</p>

                <div class="text-xs text-gray-500 mt-2 pt-2 border-t flex justify-between items-center">
                    <div class="flex flex-col space-y-0.5">
                        <span>Создана: ${created}</span>
                        <span>Дедлайн: <span class="text-gray-700">${dueDateDisplay}</span></span>
                    </div>
                    <div class="text-right">
                        <span class="block text-gray-400">Исполнитель:</span>
                        ${assignedUserHtml}
                    </div>
                </div>
            </a>
        `;
        // -----------------------------

        projectTasksList.appendChild(taskDiv);
    });
}