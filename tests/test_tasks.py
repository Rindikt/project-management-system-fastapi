from http import HTTPStatus

import pytest
from pytest_lazyfixture import lazy_fixture
from app.models.tasks import TaskPriority


@pytest.mark.parametrize(
    'auth_header_lazy, expected_status, case_description',
    [
        (lazy_fixture('auth_header_owner'), HTTPStatus.CREATED, 'Владелец проекта (Успех 201)'),
        (lazy_fixture('auth_header_member'), HTTPStatus.CREATED, 'Участник проекта (Успех 201)'),
        (lazy_fixture('auth_header_admin'), HTTPStatus.FORBIDDEN, 'Администратор системы (Отказ 403)'),
        (lazy_fixture('auth_header_second_owner'), HTTPStatus.FORBIDDEN, 'Посторонний (Отказ 403)'),
    ]
)
async def test_1_create_task_permissions(test_client, project_with_member,
                                         auth_header_lazy, expected_status,
                                         case_description, task_create_data):
    """Проверяет права на создание задачи в проекте. Только Владелец или Участник."""
    project_id = project_with_member['id']

    task_data = task_create_data.copy()

    response = test_client.post(
        f'/projects/{project_id}/tasks',
        headers=auth_header_lazy,
        json=task_data
    )
    assert response.status_code == expected_status
    if expected_status == HTTPStatus.CREATED:
        data = response.json()
        assert 'id' in data
        assert data['project_id'] == project_id


@pytest.mark.parametrize(
    'auth_header_lazy, expected_status, case_description',
    [
        (lazy_fixture('auth_header_owner'), HTTPStatus.OK, 'Владелец проекта (Успех 200)'),
        (lazy_fixture('auth_header_member'), HTTPStatus.OK, 'Участник проекта (Успех 200)'),

        # По вашей логике, Админ и Менеджер имеют право
        (lazy_fixture('auth_header_admin'), HTTPStatus.OK, 'Администратор системы (Успех 200)'),
        (lazy_fixture('auth_header_second_owner'), HTTPStatus.FORBIDDEN, 'Посторонний (Отказ 403)'),
        # (Если у вас есть фикстура для Менеджера, добавьте ее сюда)
    ]
)
async def test_2_get_tasks_list_permissions(test_client, project_with_member, # Проект, в котором есть задачи
                                            task_in_project, auth_header_lazy,
                                            expected_status, case_description):
    """Проверяет права на просмотр списка задач в проекте. Доступ: Владелец, Участник, Админ, Менеджер."""
    project_id = project_with_member['id']

    response = test_client.get(
        f'/projects/{project_id}/tasks/',
        headers=auth_header_lazy)

    assert response.status_code == expected_status
    if expected_status == HTTPStatus.OK:
        data = response.json()
        assert len(data['items']) >= 1
        assert data['items'][0]['project_id'] == project_id


@pytest.mark.parametrize(
    'auth_header_lazy, expected_status, case_description',
    [
        (lazy_fixture('auth_header_owner'), HTTPStatus.OK, 'Владелец проекта (Успех 200)'),
        (lazy_fixture('auth_header_member'), HTTPStatus.OK, 'Участник проекта (Успех 200)'),
        (lazy_fixture('auth_header_admin'), HTTPStatus.OK, 'Администратор системы (Успех 200)'),
        (lazy_fixture('auth_header_second_owner'), HTTPStatus.FORBIDDEN, 'Посторонний (Отказ 403)'),
    ]
)
async def test_3_get_single_task_permissions(test_client, task_in_project,
                                            auth_header_lazy, expected_status,
                                            case_description):
    """Проверяет права на просмотр одной задачи. Доступ: Владелец, Участник, Админ, Менеджер."""
    project_id = task_in_project['project_id']
    task_id = task_in_project['id']
    response = test_client.get(
        f'/tasks/{task_id}',
        headers=auth_header_lazy)
    assert response.status_code == expected_status
    if expected_status == HTTPStatus.OK:
        data = response.json()
        assert data['id'] == task_id
        assert data['project_id'] == project_id


@pytest.mark.parametrize(
    'auth_header_lazy, expected_status, case_description',
    [
        (lazy_fixture('auth_header_owner'), HTTPStatus.OK, 'Владелец проекта (Успех 200)'),
        (lazy_fixture('auth_header_admin'), HTTPStatus.FORBIDDEN, 'Администратор системы (Успех 200)'),
        (lazy_fixture('auth_header_second_owner'), HTTPStatus.FORBIDDEN, 'Посторонний (Отказ 403)'),
        (lazy_fixture('auth_header_member'), HTTPStatus.FORBIDDEN, 'Участник, не автор/исполнитель (Отказ 403)'),
    ]
)
async def test_4_update_task_permissions(test_client, task_in_project, task_update_data,
                                         auth_header_lazy, expected_status, case_description):
    """Проверяет права на изменение задачи. Доступ: Владелец, Автор, Исполнитель, Админ."""

    task_id = task_in_project['id']

    response = test_client.patch(
        f'/tasks/{task_id}',
        headers=auth_header_lazy,
        json=task_update_data
    )

    assert response.status_code == expected_status

    if expected_status == HTTPStatus.OK:
        data = response.json()
        assert data['title'] == 'Updated_Task_Title'
        assert data['priority'] == TaskPriority.high.value


@pytest.mark.parametrize(
    'auth_header_lazy, expected_status, case_description',
    [
        # Успешное удаление
        (lazy_fixture('auth_header_owner'), HTTPStatus.NO_CONTENT, 'Владелец проекта (Успех 204)'),
        (lazy_fixture('auth_header_admin'), HTTPStatus.NO_CONTENT, 'Администратор системы (Успех 204)'),

        # Запрет
        (lazy_fixture('auth_header_member'), HTTPStatus.FORBIDDEN, 'Участник (Отказ 403)'),
        (lazy_fixture('auth_header_second_owner'), HTTPStatus.FORBIDDEN, 'Посторонний (Отказ 403)'),
    ]
)
async def test_5_delete_task_permissions(test_client, task_in_project,  # Задача создается
                                         auth_header_lazy, expected_status, case_description):
    """Проверяет права на удаление задачи. Доступ: Владелец, Админ."""
    task_id = task_in_project['id']
    response = test_client.delete(
        f'/tasks/{task_id}',
        headers=auth_header_lazy
    )
    assert response.status_code == expected_status
    if expected_status == HTTPStatus.NO_CONTENT:
        check_response = test_client.get(
            f'/tasks/{task_id}',
            headers=auth_header_lazy)
        assert check_response.status_code == HTTPStatus.NOT_FOUND