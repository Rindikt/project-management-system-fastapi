import pytest
from http import HTTPStatus

@pytest.fixture
def create_project_data():
    return {
        'title': 'Test_Project',
        'description': 'Создание тестого проекта для теста',
        'dub_date' : '2026-09-10'}

@pytest.fixture
def owner_project(test_client, create_project_data, auth_header_owner):
    """
    Создает проект через API и возвращает его полный JSON-объект.
    """
    response = test_client.post('/projects',
                                json=create_project_data,
                                headers=auth_header_owner)
    assert response.status_code == HTTPStatus.CREATED
    return response.json()

@pytest.fixture
def second_owner_project(test_client, auth_header_second_owner, create_project_data):
    """
    Создает проект через API от имени второго пользователя и возвращает его JSON.
    """
    response = test_client.post('/projects',
                               headers=auth_header_second_owner,
                               json=create_project_data)
    assert response.status_code == HTTPStatus.CREATED
    return response.json()

@pytest.fixture
def third_project_as_member(test_client, auth_header_admin, create_project_data):
    response = test_client.post('/projects',
                                json=create_project_data,
                                headers=auth_header_admin)
    assert response.status_code == HTTPStatus.CREATED
    return response.json()



@pytest.fixture
def project_with_member(test_client, owner_project, auth_header_owner, test_user_data):
    """
    Создает проект (через owner_project) и добавляет в него тестового участника (test_user_data)
    используя API: POST /projects/{project_id}/members/{email}.

    Возвращает полный JSON-объект проекта (от owner_project).
    """

    project_id = owner_project['id']
    member_email = test_user_data.email

    response = test_client.post(
        f'/projects/{project_id}/members/{member_email}',
        headers=auth_header_owner
    )
    assert response.status_code == HTTPStatus.CREATED
    response_data = response.json()

    is_member_added = any(member['email'] == member_email for member in response_data['members'])
    assert is_member_added is True
    return owner_project

@pytest.fixture
def project_as_member(test_client, second_owner_project, auth_header_second_owner, owner_user_data):
    """
    Создает проект (через second_owner_project) и добавляет в него
    основного тестового пользователя (owner_user_data) как участника.
    Возвращает JSON-объект проекта, в котором owner_user_data является участником.
    """
    project_id = second_owner_project['id']
    member_email = owner_user_data.email

    response = test_client.post(
        f'/projects/{project_id}/members/{member_email}',
        headers=auth_header_second_owner)

    assert response.status_code == HTTPStatus.CREATED

    response = test_client.get(
        f'/projects/{project_id}',
        headers=auth_header_second_owner
    )

    assert response.status_code == HTTPStatus.OK
    return response.json()