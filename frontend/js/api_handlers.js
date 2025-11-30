// --- ФУНКЦИЯ РЕДАКТИРОВАНИЯ ПРОЕКТА (ИСПРАВЛЕН МЕТОД: PUT -> PATCH) ---
async function handleEditProject(event) {
    event.preventDefault();

    const currentProjectId = getProjectIdFromUrl();
    if (!currentProjectId) {
        setStatus('Ошибка: ID проекта не найден.', 'error');
        return;
    }

    // Собираем данные формы
    const title = editProjectName.value;
    const description = editProjectDescription.value;
    const dueDate = editProjectDueDate.value; // Получаем значение даты

    // Формируем тело запроса
    const requestBody = {
        title: title,
        description: description,
        // Если дата пустая строка, отправляем null, иначе отправляем дату
        dub_date: dueDate || null
    };

    setStatus('Сохранение изменений...', 'loading');

    try {
        const response = await fetch(`${API_BASE_URL}/projects/${currentProjectId}`, {
            // !!! ИСПРАВЛЕНИЕ: Используем PATCH вместо PUT
            method: 'PATCH',
            headers: {
                'Authorization': `Bearer ${ACCESS_TOKEN}`,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestBody)
        });

        if (response.ok) {
            const updatedProject = await response.json();
            setStatus('Проект успешно обновлен.', 'success');

            // Скрыть форму и показать режим просмотра
            projectEditFormCard.classList.add('hidden');
            projectViewCard.classList.remove('hidden');

            // Обновить данные на странице
            renderProjectDetails(updatedProject);

        } else {
            const errorData = await response.json();
            setStatus(`Ошибка редактирования: ${errorData.detail || response.statusText}`, 'error');
        }
    } catch (error) {
        setStatus(`Сетевая ошибка при редактировании: ${error.message}`, 'error');
    }
}

// --- ФУНКЦИЯ УДАЛЕНИЯ ПРОЕКТА ---
async function handleDeleteProject() {
    if (!projectDetailContent.dataset.confirmDelete) {
        setStatus('Нажмите "Удалить Проект" еще раз для подтверждения. Это действие необратимо.', true);
        projectDetailContent.dataset.confirmDelete = 'true';
        setTimeout(() => {
            if (projectDetailContent.dataset.confirmDelete) {
                delete projectDetailContent.dataset.confirmDelete;
                setStatus('Действие отменено.', false);
            }
        }, 3000);
        return;
    }

    delete projectDetailContent.dataset.confirmDelete;
    projectDetailContent.classList.add('opacity-50', 'pointer-events-none');

    try {
        const response = await fetch(`${API_BASE_URL}/projects/${currentProjectId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${ACCESS_TOKEN}`,
            },
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ detail: 'Неизвестная ошибка сервера.' }));
            throw new Error(errorData.detail || 'Не удалось удалить проект. Возможно, у вас нет прав.');
        }

        setStatus('Проект успешно удален. Возврат к списку...', false);
        setTimeout(() => window.location.href = 'index.html', 1500);

    } catch (error) {
        setStatus('Ошибка удаления: ' + error.message, true);
        projectDetailContent.classList.remove('opacity-50', 'pointer-events-none');
    }
}

// --- ФУНКЦИЯ ДОБАВЛЕНИЯ УЧАСТНИКА ---
async function handleAddMember(e) {
    e.preventDefault();

    const emailInput = document.getElementById('member-email-input');
    const email = emailInput.value.trim();

    if (!email || !currentProjectId) {
        setStatus('Email и ID проекта должны быть указаны.', true);
        return;
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
        setStatus('Пожалуйста, введите корректный адрес электронной почты.', true);
        return;
    }

    const submitButton = addMemberForm.querySelector('button[type="submit"]');
    submitButton.disabled = true;
    submitButton.textContent = 'Добавляем...';
    submitButton.classList.add('opacity-75');

    try {
        const response = await fetch(`${API_BASE_URL}/projects/${currentProjectId}/members/${email}`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${ACCESS_TOKEN}`,
                'Content-Type': 'application/json',
            },
        });

        if (!response.ok) {
            let errorDetail = 'Неизвестная ошибка.';
            try {
                const errorData = await response.json();
                errorDetail = errorData.detail || `Ошибка сервера (${response.status}): Не удалось прочитать ответ.`;
            } catch (e) {
                errorDetail = `Ошибка сервера (${response.status}): ${response.statusText}`;
            }

            throw new Error(errorDetail);
        }

        const project = await response.json();
        renderProjectDetails(project); // Обновляем данные проекта и рендерим все заново

        setStatus(`Участник с email "${email}" успешно добавлен.`, false);
        emailInput.value = '';

    } catch (error) {
        setStatus('Ошибка добавления участника: ' + error.message, true);
    } finally {
        submitButton.disabled = false;
        submitButton.textContent = 'Добавить Участника';
        submitButton.classList.remove('opacity-75');
    }
}

// --- ФУНКЦИЯ УДАЛЕНИЯ УЧАСТНИКА (ИСПРАВЛЕНО НА ID) ---
async function handleRemoveMember(userId) {
    const currentProjectId = getProjectIdFromUrl();
    if (!currentProjectId) {
        setStatus('Ошибка: ID проекта не найден.', 'error');
        return;
    }

    if (!confirm('Вы уверены, что хотите удалить этого участника из проекта?')) {
        return;
    }

    setStatus('Удаление участника...', 'loading');

    // !!! ИЗМЕНЕНИЕ 3: Используем ID в URL
    try {
        const response = await fetch(`${API_BASE_URL}/projects/${currentProjectId}/members/${userId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${ACCESS_TOKEN}`,
            },
        });

        if (response.ok) {
            setStatus('Участник успешно удален.', 'success');
            // Перезагрузка деталей проекта для обновления списка
            await fetchProjectDetail();
        } else {
            const errorData = await response.json();
            setStatus(`Ошибка при удалении: ${errorData.detail || response.statusText}`, 'error');
        }
    } catch (error) {
        setStatus(`Сетевая ошибка: ${error.message}`, 'error');
    }
}

// TODO: ФУНКЦИЯ СОЗДАНИЯ ЗАДАЧИ
async function handleCreateTask(e) {
    e.preventDefault();

    const title = taskTitleInput.value.trim();
    const description = taskDescriptionInput.value.trim();
    const priority = taskPrioritySelect.value;
    const assignedToEmail = taskAssignedToSelect.value || null; // Если пусто, то null
    const dueDate = taskDueDateInput.value || null;

    if (!currentProjectId || !title || description.length < 10) {
        setStatus('Пожалуйста, заполните название и описание (минимум 10 символов).', true);
        return;
    }

    const newTask = {
        title: title,
        description: description,
        priority: priority,
        // due_date: (Если у вас есть поле due_date для задач, добавьте его сюда)
        due_date: dueDate,
        assigned_to_email: assignedToEmail, // Используем email, как требует ваш API
    };

    const submitButton = createTaskForm.querySelector('button[type="submit"]');
    submitButton.disabled = true;
    submitButton.textContent = 'Создание...';
    submitButton.classList.add('opacity-75');


    try {
        const response = await fetch(`${API_BASE_URL}/projects/${currentProjectId}/tasks`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${ACCESS_TOKEN}`,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(newTask)
        });

        if (!response.ok) {
            let errorDetail = 'Неизвестная ошибка создания задачи.';
            try {
                const errorData = await response.json();
                errorDetail = errorData.detail || `Ошибка сервера (${response.status}): Не удалось прочитать ответ.`;
            } catch (e) {
                errorDetail = `Ошибка сервера (${response.status}): ${response.statusText}`;
            }

            throw new Error(errorDetail);
        }

        setStatus('Задача успешно создана!', false);
        createTaskForm.reset(); // Очищаем форму
        await fetchProjectDetail(); // Перезагружаем проект, чтобы увидеть новую задачу

    } catch (error) {
        setStatus('Ошибка создания задачи: ' + error.message, true);
    } finally {
        submitButton.disabled = false;
        submitButton.textContent = 'Создать Задачу';
        submitButton.classList.remove('opacity-75');
    }
}
// --- ФУНКЦИЯ РЕДАКТИРОВАНИЯ ЗАДАЧИ ---
async function handleEditTask(event) {
    event.preventDefault();

    // ПРОВЕРКА: Используем глобальную переменную currentTaskId из task_detail.js
    if (!currentTaskId) {
        setStatus('Ошибка: ID задачи не найден. Пожалуйста, перезагрузите страницу.', true);
        return;
    }

    // Собираем данные формы редактирования (элементы определены в task_detail.js)
    const title = editTaskTitle.value.trim();
    const description = editTaskDescription.value.trim();
    const priority = editTaskPriority.value;
    const status = editTaskStatus.value;
    const dueDate = editTaskDueDate.value || null; // Если поле пустое, отправляем null

    // Формируем тело запроса (включаем только те поля, которые могут быть изменены)
    const requestBody = {
        title: title,
        description: description,
        priority: priority,
        status: status,
        due_date: dueDate
        // Если вы добавите поле assigned_to_email для редактирования, его нужно добавить сюда
    };

    // Включаем или выключаем кнопку сохранения
    const submitButton = editTaskForm.querySelector('button[type="submit"]');
    submitButton.disabled = true;
    submitButton.textContent = 'Сохранение...';
    submitButton.classList.add('opacity-75');

    setStatus('Сохранение изменений задачи...', false);

    try {
        const response = await fetch(`${API_BASE_URL}/tasks/${currentTaskId}`, {
            method: 'PATCH',
            headers: {
                'Authorization': `Bearer ${ACCESS_TOKEN}`,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestBody)
        });

        if (response.ok) {
            const updatedTask = await response.json();
            setStatus('Задача успешно обновлена.', false);

            // 1. Обновляем UI
            renderTaskDetails(updatedTask);

            // 2. Переключаем обратно в режим просмотра (эта функция в task_detail.js)
            toggleEditMode(false);

        } else {
            const errorData = await response.json();
            setStatus(`Ошибка редактирования: ${errorData.detail || response.statusText}`, true);
        }
    } catch (error) {
        setStatus(`Сетевая ошибка при редактировании: ${error.message}`, true);
    } finally {
        submitButton.disabled = false;
        submitButton.textContent = 'Сохранить';
        submitButton.classList.remove('opacity-75');
    }
}