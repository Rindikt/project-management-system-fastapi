from enum import member
from http import HTTPStatus
import pytest
from pytest_lazyfixture import lazy_fixture

from tests.fixtures.project_fixtures import project_with_member

FIRST_ID = 1

def test_create_project_success(test_client,auth_header_owner, create_project_data):
    """
    Проверяет успешное создание нового проекта аутентифицированным пользователем.
    """

    response = test_client.post(
        '/projects',
        json=create_project_data,
        headers=auth_header_owner
    )
    print(response.json())
    assert response.status_code == HTTPStatus.CREATED

    data = response.json()
    assert 'id' in data

    assert data['title'] == create_project_data['title']
    assert data['description'] == create_project_data['description']

    assert 'owner' in data
    assert data['owner']['id'] == FIRST_ID


@pytest.mark.parametrize(
    'auth_header_lazy, project_fixture_lazy, case_description',
    [
        (lazy_fixture('auth_header_owner'), lazy_fixture('owner_project'), 'Владелец проекта'),

        # Для Участника и Администратора используем проект, в котором участник уже добавлен:
        (lazy_fixture('auth_header_member'), lazy_fixture('project_with_member'), 'Участник проекта'),
        (lazy_fixture('auth_header_admin'), lazy_fixture('project_with_member'), 'Администратор системы'),
    ]
)
def test_get_project_id_success_roles(test_client, auth_header_lazy, project_fixture_lazy, case_description):
    """
    Проверяет успешное получение проекта ролями: Владелец, Участник и Администратор.

    auth_header_lazy: Фикстура заголовка (будет разрешена Pytest).
    project_fixture_lazy: Фикстура проекта (будет разрешена Pytest).
    """
    print(f"\nТестирование успешного доступа: {case_description}")

    project_id = project_fixture_lazy['id']

    response = test_client.get(
        f'/projects/{project_id}',
        headers=auth_header_lazy
    )

    assert response.status_code == HTTPStatus.OK

    data = response.json()
    assert data['id'] == project_id
    assert 'title' in data
    assert 'owner' in data

@pytest.mark.parametrize(
    'auth_header_lazy, expected_status, case_description',
    [
        (lazy_fixture('auth_header_second_owner'), HTTPStatus.FORBIDDEN,'Посторонний владелец (403)'),
        (None, HTTPStatus.UNAUTHORIZED, 'Неавторизованный пользователь (401)')
    ])
async def test_get_project_id_forbidden_access(
        test_client, owner_project,
        auth_header_lazy, expected_status, case_description):
    """
    Проверяет, что неавторизованные или посторонние пользователи получают 403 Forbidden.
    """
    print(f"\nТестирование запрета доступа: {case_description}")
    project_id = owner_project['id']
    response = test_client.get(
        f'/projects/{project_id}',
    headers=auth_header_lazy if auth_header_lazy else None)

    assert response.status_code == expected_status
    if expected_status == HTTPStatus.FORBIDDEN:
        assert 'detail' in response.json()

async def test_get_projects_admin_sees_all(test_client, auth_header_admin,
                                           project_with_member, second_owner_project):
    """
     Администратор должен видеть все существующие проекты.
    """
    response = test_client.get(
        '/projects',
        headers=auth_header_admin
    )
    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert len(data) >= 2

    project_ids = [p['id'] for p in data]
    assert project_with_member['id'] in project_ids
    assert second_owner_project['id'] in project_ids

async def test_get_projects_owner_sees_only_relevant(
        test_client,
        auth_header_owner,
        owner_project,
        second_owner_project,
        third_project_as_member,
        project_as_member):
    """
    Пользователь видит только те проекты, где он владелец ИЛИ участник.
    """
    response = test_client.get(
        '/projects',
        headers=auth_header_owner
    )
    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert len(data) >= 2

    project_ids = [p['id'] for p in data]

    assert owner_project['id'] in project_ids
    assert project_as_member['id'] in project_ids
    assert third_project_as_member['id'] not in project_ids


@pytest.mark.parametrize(
    'auth_header_lazy, expected_status, case_description',
    [
        (lazy_fixture('auth_header_owner'), HTTPStatus.OK, 'Владелец (Успех 200)'),
        (lazy_fixture('auth_header_member'), HTTPStatus.FORBIDDEN, 'Участник (Отказ 403)'),
        (lazy_fixture('auth_header_admin'), HTTPStatus.FORBIDDEN, 'Администратор (Отказ 403)'),
        (lazy_fixture('auth_header_second_owner'), HTTPStatus.FORBIDDEN, 'Посторонний (Отказ 403)')
    ]
)
async def test_update_project_permissions(test_client, project_with_member,
                                          create_project_data, auth_header_lazy,
                                          expected_status, case_description):
    """Проверяет права на обновление проекта."""
    project_id = project_with_member['id']
    update_data = {"title": "Новое название проекта"}

    response = test_client.patch(f'/projects/{project_id}',
                                 json=update_data,
                                 headers=auth_header_lazy,)
    assert response.status_code == expected_status

    if expected_status == HTTPStatus.OK:
        data = response.json()
        assert data['title'] == update_data['title']


@pytest.mark.parametrize(
    'auth_header_lazy, expected_status, case_description',
    [
        (lazy_fixture('auth_header_owner'), HTTPStatus.CREATED, 'Владелец (Успех 200)'),
        (lazy_fixture('auth_header_member'), HTTPStatus.FORBIDDEN, 'Участник (Отказ 403)'),
        (lazy_fixture('auth_header_admin'), HTTPStatus.FORBIDDEN, 'Администратор (Отказ 403)'),
        (lazy_fixture('auth_header_second_owner'), HTTPStatus.FORBIDDEN, 'Посторонний (Отказ 403)')
    ]
)
async def test_add_member_permissions(test_client, owner_project,
                                      auth_header_lazy, expected_status,
                                      case_description,test_user_data ):
    """Проверяет права на добавление участника в проект."""
    project_id = owner_project['id']
    member_email = test_user_data.email
    response = test_client.post(
        f'/projects/{project_id}/members/{member_email}',
        headers=auth_header_lazy,
    )
    assert response.status_code == expected_status
    if expected_status == HTTPStatus.OK:
        data = response.json()
        assert any(member['email'] == member_email for member in data['members'])


@pytest.mark.parametrize(
    'auth_header_lazy, expected_status, case_description',
    [
        (lazy_fixture('auth_header_owner'), HTTPStatus.OK, 'Владелец (Успех 200)'),
        (lazy_fixture('auth_header_member'), HTTPStatus.FORBIDDEN, 'Участник (Отказ 403)'),
        (lazy_fixture('auth_header_admin'), HTTPStatus.FORBIDDEN, 'Администратор (Отказ 403)'),
        (lazy_fixture('auth_header_second_owner'), HTTPStatus.FORBIDDEN, 'Посторонний (Отказ 403)')
    ]
)
async def test_remove_member_permissions(test_client, project_with_member,
                                         auth_header_lazy, expected_status,
                                         case_description,test_user_data):
    """Проверяет права на удаление участника из проекта."""

    project_id = project_with_member['id']
    member_to_remove_id = test_user_data.id
    response = test_client.delete(
        f'/projects/{project_id}/members/{member_to_remove_id}',
        headers=auth_header_lazy,
    )
    assert response.status_code == expected_status
    if expected_status == HTTPStatus.OK:
        data = response.json()
        assert not any(member['email'] == member_to_remove_id for member in data['members'])


@pytest.mark.parametrize(
    'auth_header_lazy, expected_status, case_description',
    [
        (lazy_fixture('auth_header_owner'), HTTPStatus.NO_CONTENT, 'Владелец (Успех 200)'),
        (lazy_fixture('auth_header_member'), HTTPStatus.FORBIDDEN, 'Участник (Отказ 403)'),
        (lazy_fixture('auth_header_admin'), HTTPStatus.NO_CONTENT, 'Администратор (Успех 200)'),
        (lazy_fixture('auth_header_second_owner'), HTTPStatus.FORBIDDEN, 'Посторонний (Отказ 403)')
    ]
)
async def test_delete_project_permissions(test_client, owner_project,
                                          auth_header_lazy, expected_status,
                                          case_description
):
    """Проверяет права на удаление проекта."""
    project_id = owner_project['id']
    response = test_client.delete(
        f'/projects/{project_id}',
        headers=auth_header_lazy,
    )
    assert response.status_code == expected_status
    if expected_status == HTTPStatus.NO_CONTENT:
        get_response = test_client.get(
            f'/projects/{project_id}',
            headers=auth_header_lazy)
        assert get_response.status_code == HTTPStatus.NOT_FOUND

