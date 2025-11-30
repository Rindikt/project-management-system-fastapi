import pytest
from http import HTTPStatus
from pytest_lazyfixture import lazy_fixture

from app.auth import verify_password

AUTH_CASES = [
    (lazy_fixture('auth_header_member'), HTTPStatus.OK, 'member@test.com'),
    (lazy_fixture('auth_header_owner'), HTTPStatus.OK, 'owner@test.com'),
    (lazy_fixture('auth_header_admin'), HTTPStatus.OK, 'admin@test.com'),
    (None, 401, None),
]
@pytest.mark.parametrize('headers, expected_status, expected_email',
    AUTH_CASES)
def test_get_my_profile_access(test_client, headers, expected_status, expected_email):
    resource = test_client.get('/users/me', headers=headers)

    assert resource.status_code == expected_status

    if expected_status == HTTPStatus.OK:
        data = resource.json()

        assert data['email'] == expected_email


def test_register_user_success(test_client):
    """
    Проверяет успешную регистрацию нового пользователя через роут POST /users.
    """
    new_user_data = {
        'email':'new_user@test.com',
        'password':'StrongPassword123',
        'first_name':'Сильвана',
        'last_name': 'Ветрокрылая',
        'position': 'Предводительница_следопытов'
    }

    response = test_client.post('/users', json=new_user_data)
    assert response.status_code == HTTPStatus.CREATED
    data = response.json()
    assert data['email'] == new_user_data['email']
    assert 'id' in data
    assert data['role'] == 'member'


def test_login_user_success(test_client, owner_user_data):
    """
    Проверяет успешную аутентификацию по email/паролю
    и получение access_token и refresh_token.
    """

    login_data = {
        'username': owner_user_data.email,
        'password': '12345Qwert'
    }

    response = test_client.post('/users/token', data=login_data)
    assert response.status_code == 200

    data = response.json()
    assert 'access_token' in data
    assert 'refresh_token' in data
    assert data['token_type'] == 'bearer'

    assert len(data['access_token']) > 10


def test_register_user_duplicate_email(test_client):
    """
    Проверяет, что при повторной регистрации с существующим email 
    возвращается статус 409 Conflict (или 400 Bad Request, в зависимости от API).
    """
    duplicate_user_data = {
        'email': 'new_user@test.com',
        'password': 'AnotherPassword123',
        'first_name': 'Дубликат',
        'last_name': 'Пользователь',
        'position': 'Cloner'
    }

    test_client.post('/users', json=duplicate_user_data)

    response = test_client.post('/users', json=duplicate_user_data)

    assert response.status_code == 409

    data = response.json()
    assert data['detail'] == 'Email already registered'


LOGIN_INVALID_CASES = [
    ('non_existent@user.com', 'SomePassword123', 'Неверный email'),
    ('owner@test.com', 'WrongPassword123', 'Неверный пароль'),
]
@pytest.mark.parametrize('email, password, case_description', LOGIN_INVALID_CASES)
def test_login_user_invalid_credentials(test_client, owner_user_data, email, password, case_description):
    """
    Проверяет, что аутентификация завершается неудачей при неверных учетных данных.
    """
    if email == 'owner@test.com':
        login_email = owner_user_data.email
    else:
        login_email = email
    login_data = {
        'username': login_email,
        'password': password
    }

    response = test_client.post('/users/token', data=login_data)

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    data = response.json()
    assert data['detail'] == 'Incorrect email or password'

























