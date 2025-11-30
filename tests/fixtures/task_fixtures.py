from http import HTTPStatus

import pytest
from app.models.tasks import TaskPriority, TaskStatus


@pytest.fixture
def task_create_data():
    return {
        'title': 'New_task',
        'description': 'New_description',
        'priority': TaskPriority.medium.value,
        'due_date': '2021-01-10',
    }

@pytest.fixture
def task_update_data():
    return {
        'title': 'Updated_Task_Title',
        'description': 'Description has been updated by the test.',
        'priority': TaskPriority.high.value, # Сменили с medium
        'status': TaskStatus.in_progress.value, # Сменили с new
        'due_date': '2027-12-31',
    }


@pytest.fixture
def task_in_project(project_with_member, task_create_data, test_client, auth_header_owner):

    task_data = task_create_data.copy()
    project_id = project_with_member['id']

    response = test_client.post(
        f'/projects/{project_id}/tasks',
        headers=auth_header_owner,
        json=task_data
    )

    assert response.status_code == HTTPStatus.CREATED
    return response.json()