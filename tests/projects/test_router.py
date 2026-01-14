import pytest
from fastapi import status
import uuid
from datetime import datetime, timedelta


class TestCreateProjectEndpoint:
    """Test POST /project/ endpoint."""

    def test_create_project_success(self, client_with_auth):
        """Test successful project creation."""
        response = client_with_auth.post(
            "/project/",
            json={"name": "Website Redesign"},
            cookies={"access_token": client_with_auth.test_token},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Website Redesign"
        assert "id" in data
        assert data["user_id"] == str(client_with_auth.test_user.id)
        assert data["completed"] is False  # Default value

    def test_create_project_with_deadline(self, client_with_auth):
        """Test creating project with deadline."""
        future_date = (datetime.utcnow() + timedelta(days=30)).isoformat()
        response = client_with_auth.post(
            "/project/",
            json={"name": "Q1 Campaign", "deadline": future_date},
            cookies={"access_token": client_with_auth.test_token},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Q1 Campaign"
        assert data["deadline"] is not None

    def test_create_project_with_description(self, client_with_auth):
        """Test creating project with description."""
        response = client_with_auth.post(
            "/project/",
            json={"name": "Website Redesign", "description": "Complete redesign of the company website"},
            cookies={"access_token": client_with_auth.test_token},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Website Redesign"
        assert data["description"] == "Complete redesign of the company website"

    def test_create_project_mark_completed(self, client_with_auth):
        """Test creating project with completed status."""
        response = client_with_auth.post(
            "/project/",
            json={"name": "Finished Project", "completed": True},
            cookies={"access_token": client_with_auth.test_token},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Finished Project"
        assert data["completed"] is True

    def test_create_project_with_client(self, client_with_auth):
        """Test creating project with client reference."""
        # First create a client
        client_response = client_with_auth.post(
            "/client/",
            json={"name": "Acme Corp"},
            cookies={"access_token": client_with_auth.test_token},
        )
        client_id = client_response.json()["id"]
        
        # Create project for that client
        response = client_with_auth.post(
            "/project/",
            json={"name": "Acme Website", "client_id": client_id},
            cookies={"access_token": client_with_auth.test_token},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["client_id"] == client_id

    def test_create_project_missing_name(self, client_with_auth):
        """Test that missing name returns 422."""
        response = client_with_auth.post(
            "/project/",
            json={},
            cookies={"access_token": client_with_auth.test_token},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_project_no_auth(self, client_with_auth):
        """Test that creating project without auth returns 401."""
        response = client_with_auth.post(
            "/project/",
            json={"name": "Unauthorized Project"},
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestGetProjectEndpoint:
    """Test GET /project/get/{project_id} endpoint."""

    def test_get_project_success(self, client_with_auth):
        """Test successfully retrieving a project."""
        # Create a project first
        create_response = client_with_auth.post(
            "/project/",
            json={"name": "Test Project"},
            cookies={"access_token": client_with_auth.test_token},
        )
        project_id = create_response.json()["id"]
        
        # Get the project
        response = client_with_auth.get(
            f"/project/get/{project_id}",
            cookies={"access_token": client_with_auth.test_token},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Test Project"
        assert data["id"] == project_id

    def test_get_project_not_found(self, client_with_auth):
        """Test getting non-existent project returns 404."""
        fake_id = str(uuid.uuid4())
        
        response = client_with_auth.get(
            f"/project/get/{fake_id}",
            cookies={"access_token": client_with_auth.test_token},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"].lower()

    def test_get_project_no_auth(self, client_with_auth):
        """Test that getting project without auth returns 401."""
        fake_id = str(uuid.uuid4())
        
        response = client_with_auth.get(f"/project/get/{fake_id}")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestListProjectsEndpoint:
    """Test GET /project/all/ endpoint."""

    def test_list_projects_success(self, client_with_auth):
        """Test listing all projects for a user."""
        # Create multiple projects
        client_with_auth.post(
            "/project/",
            json={"name": "Project 1"},
            cookies={"access_token": client_with_auth.test_token},
        )
        client_with_auth.post(
            "/project/",
            json={"name": "Project 2"},
            cookies={"access_token": client_with_auth.test_token},
        )
        
        # List all projects
        response = client_with_auth.get(
            "/project/all/",
            cookies={"access_token": client_with_auth.test_token},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 2
        assert data[0]["name"] == "Project 1"
        assert data[1]["name"] == "Project 2"

    def test_list_projects_empty(self, client_with_auth):
        """Test listing projects when user has none."""
        response = client_with_auth.get(
            "/project/all/",
            cookies={"access_token": client_with_auth.test_token},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 0

    def test_list_projects_no_auth(self, client_with_auth):
        """Test that listing without auth returns 401."""
        response = client_with_auth.get("/project/all/")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestListClientProjectsEndpoint:
    """Test GET /project/client/{client_id} endpoint."""

    def test_list_client_projects_success(self, client_with_auth):
        """Test listing all projects for a specific client."""
        # Create a client
        client_response = client_with_auth.post(
            "/client/",
            json={"name": "Acme Corp"},
            cookies={"access_token": client_with_auth.test_token},
        )
        client_id = client_response.json()["id"]
        
        # Create projects for that client
        client_with_auth.post(
            "/project/",
            json={"name": "Website Redesign", "client_id": client_id},
            cookies={"access_token": client_with_auth.test_token},
        )
        client_with_auth.post(
            "/project/",
            json={"name": "Logo Design", "client_id": client_id},
            cookies={"access_token": client_with_auth.test_token},
        )
        
        # List client's projects
        response = client_with_auth.get(
            f"/project/client/{client_id}",
            cookies={"access_token": client_with_auth.test_token},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 2
        assert all(p["client_id"] == client_id for p in data)

    def test_list_client_projects_empty(self, client_with_auth):
        """Test listing projects for client with no projects."""
        # Create a client
        client_response = client_with_auth.post(
            "/client/",
            json={"name": "Empty Client"},
            cookies={"access_token": client_with_auth.test_token},
        )
        client_id = client_response.json()["id"]
        
        response = client_with_auth.get(
            f"/project/client/{client_id}",
            cookies={"access_token": client_with_auth.test_token},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 0


class TestUpdateProjectEndpoint:
    """Test PATCH /project/{project_id} endpoint."""

    def test_update_project_name(self, client_with_auth):
        """Test updating project name."""
        # Create a project
        create_response = client_with_auth.post(
            "/project/",
            json={"name": "Old Name"},
            cookies={"access_token": client_with_auth.test_token},
        )
        project_id = create_response.json()["id"]
        
        # Update it
        response = client_with_auth.patch(
            f"/project/{project_id}",
            json={"name": "New Name"},
            cookies={"access_token": client_with_auth.test_token},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "New Name"

    def test_update_project_deadline(self, client_with_auth):
        """Test updating project deadline."""
        # Create a project
        create_response = client_with_auth.post(
            "/project/",
            json={"name": "Test Project"},
            cookies={"access_token": client_with_auth.test_token},
        )
        project_id = create_response.json()["id"]
        
        # Update deadline
        future_date = (datetime.utcnow() + timedelta(days=60)).isoformat()
        response = client_with_auth.patch(
            f"/project/{project_id}",
            json={"deadline": future_date},
            cookies={"access_token": client_with_auth.test_token},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["deadline"] is not None

    def test_update_project_description(self, client_with_auth):
        """Test updating project description."""
        # Create a project
        create_response = client_with_auth.post(
            "/project/",
            json={"name": "Test Project"},
            cookies={"access_token": client_with_auth.test_token},
        )
        project_id = create_response.json()["id"]
        
        # Update description
        response = client_with_auth.patch(
            f"/project/{project_id}",
            json={"description": "Updated project description"},
            cookies={"access_token": client_with_auth.test_token},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["description"] == "Updated project description"

    def test_update_project_completed(self, client_with_auth):
        """Test updating project completed status."""
        # Create a project
        create_response = client_with_auth.post(
            "/project/",
            json={"name": "Test Project"},
            cookies={"access_token": client_with_auth.test_token},
        )
        project_id = create_response.json()["id"]
        
        # Mark as completed
        response = client_with_auth.patch(
            f"/project/{project_id}",
            json={"completed": True},
            cookies={"access_token": client_with_auth.test_token},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["completed"] is True

    def test_update_project_not_found(self, client_with_auth):
        """Test updating non-existent project returns 404."""
        fake_id = str(uuid.uuid4())
        
        response = client_with_auth.patch(
            f"/project/{fake_id}",
            json={"name": "New Name"},
            cookies={"access_token": client_with_auth.test_token},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestDeleteProjectEndpoint:
    """Test DELETE /project/{project_id} endpoint."""

    def test_delete_project_success(self, client_with_auth):
        """Test successfully deleting a project."""
        # Create a project
        create_response = client_with_auth.post(
            "/project/",
            json={"name": "Project to Delete"},
            cookies={"access_token": client_with_auth.test_token},
        )
        project_id = create_response.json()["id"]
        
        # Delete it
        response = client_with_auth.delete(
            f"/project/{project_id}",
            cookies={"access_token": client_with_auth.test_token},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == project_id
        
        # Verify it's gone
        get_response = client_with_auth.get(
            f"/project/get/{project_id}",
            cookies={"access_token": client_with_auth.test_token},
        )
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_project_not_found(self, client_with_auth):
        """Test deleting non-existent project returns 404."""
        fake_id = str(uuid.uuid4())
        
        response = client_with_auth.delete(
            f"/project/{fake_id}",
            cookies={"access_token": client_with_auth.test_token},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestCreateTaskEndpoint:
    """Test POST /project/task/ endpoint."""

    def test_create_task_success(self, client_with_auth):
        """Test successful task creation."""
        # Create a project first
        project_response = client_with_auth.post(
            "/project/",
            json={"name": "Test Project"},
            cookies={"access_token": client_with_auth.test_token},
        )
        project_id = project_response.json()["id"]
        
        # Create a task
        response = client_with_auth.post(
            "/project/task/",
            json={"name": "Build UI", "project_id": project_id},
            cookies={"access_token": client_with_auth.test_token},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Build UI"
        assert data["project_id"] == project_id
        assert data["user_id"] == str(client_with_auth.test_user.id)

    def test_create_task_with_deadline(self, client_with_auth):
        """Test creating task with deadline."""
        # Create a project first
        project_response = client_with_auth.post(
            "/project/",
            json={"name": "Test Project"},
            cookies={"access_token": client_with_auth.test_token},
        )
        project_id = project_response.json()["id"]
        
        # Create task with deadline
        future_date = (datetime.utcnow() + timedelta(days=7)).isoformat()
        response = client_with_auth.post(
            "/project/task/",
            json={"name": "Quick Task", "project_id": project_id, "deadline": future_date},
            cookies={"access_token": client_with_auth.test_token},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["deadline"] is not None

    def test_create_task_missing_name(self, client_with_auth):
        """Test that missing task name returns 422."""
        # Create a project first
        project_response = client_with_auth.post(
            "/project/",
            json={"name": "Test Project"},
            cookies={"access_token": client_with_auth.test_token},
        )
        project_id = project_response.json()["id"]
        
        response = client_with_auth.post(
            "/project/task/",
            json={"project_id": project_id},
            cookies={"access_token": client_with_auth.test_token},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_task_no_auth(self, client_with_auth):
        """Test that creating task without auth returns 401."""
        fake_id = str(uuid.uuid4())
        
        response = client_with_auth.post(
            "/project/task/",
            json={"name": "Unauthorized Task", "project_id": fake_id},
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestListProjectTasksEndpoint:
    """Test GET /project/get/{project_id}/tasks endpoint."""

    def test_list_project_tasks_success(self, client_with_auth):
        """Test listing all tasks for a project."""
        # Create a project
        project_response = client_with_auth.post(
            "/project/",
            json={"name": "Test Project"},
            cookies={"access_token": client_with_auth.test_token},
        )
        project_id = project_response.json()["id"]
        
        # Create multiple tasks
        client_with_auth.post(
            "/project/task/",
            json={"name": "Task 1", "project_id": project_id},
            cookies={"access_token": client_with_auth.test_token},
        )
        client_with_auth.post(
            "/project/task/",
            json={"name": "Task 2", "project_id": project_id},
            cookies={"access_token": client_with_auth.test_token},
        )
        
        # List tasks
        response = client_with_auth.get(
            f"/project/get/{project_id}/tasks",
            cookies={"access_token": client_with_auth.test_token},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 2
        assert data[0]["name"] == "Task 1"
        assert data[1]["name"] == "Task 2"

    def test_list_project_tasks_empty(self, client_with_auth):
        """Test listing tasks for project with no tasks."""
        # Create a project
        project_response = client_with_auth.post(
            "/project/",
            json={"name": "Empty Project"},
            cookies={"access_token": client_with_auth.test_token},
        )
        project_id = project_response.json()["id"]
        
        response = client_with_auth.get(
            f"/project/get/{project_id}/tasks",
            cookies={"access_token": client_with_auth.test_token},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 0

    def test_list_project_tasks_no_auth(self, client_with_auth):
        """Test that listing without auth returns 401."""
        fake_id = str(uuid.uuid4())
        
        response = client_with_auth.get(f"/project/get/{fake_id}/tasks")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestUpdateTaskEndpoint:
    """Test PATCH /project/task/{task_id} endpoint."""

    def test_update_task_name(self, client_with_auth):
        """Test updating task name."""
        # Create project and task
        project_response = client_with_auth.post(
            "/project/",
            json={"name": "Test Project"},
            cookies={"access_token": client_with_auth.test_token},
        )
        project_id = project_response.json()["id"]
        
        task_response = client_with_auth.post(
            "/project/task/",
            json={"name": "Old Task Name", "project_id": project_id},
            cookies={"access_token": client_with_auth.test_token},
        )
        task_id = task_response.json()["id"]
        
        # Update task
        response = client_with_auth.patch(
            f"/project/task/{task_id}",
            json={"name": "New Task Name"},
            cookies={"access_token": client_with_auth.test_token},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "New Task Name"

    def test_update_task_deadline(self, client_with_auth):
        """Test updating task deadline."""
        # Create project and task
        project_response = client_with_auth.post(
            "/project/",
            json={"name": "Test Project"},
            cookies={"access_token": client_with_auth.test_token},
        )
        project_id = project_response.json()["id"]
        
        task_response = client_with_auth.post(
            "/project/task/",
            json={"name": "Test Task", "project_id": project_id},
            cookies={"access_token": client_with_auth.test_token},
        )
        task_id = task_response.json()["id"]
        
        # Update deadline
        future_date = (datetime.utcnow() + timedelta(days=14)).isoformat()
        response = client_with_auth.patch(
            f"/project/task/{task_id}",
            json={"deadline": future_date},
            cookies={"access_token": client_with_auth.test_token},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["deadline"] is not None

    def test_update_task_not_found(self, client_with_auth):
        """Test updating non-existent task returns 404."""
        fake_id = str(uuid.uuid4())
        
        response = client_with_auth.patch(
            f"/project/task/{fake_id}",
            json={"name": "New Name"},
            cookies={"access_token": client_with_auth.test_token},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestDeleteTaskEndpoint:
    """Test DELETE /project/task/{task_id} endpoint."""

    def test_delete_task_success(self, client_with_auth):
        """Test successfully deleting a task."""
        # Create project and task
        project_response = client_with_auth.post(
            "/project/",
            json={"name": "Test Project"},
            cookies={"access_token": client_with_auth.test_token},
        )
        project_id = project_response.json()["id"]
        
        task_response = client_with_auth.post(
            "/project/task/",
            json={"name": "Task to Delete", "project_id": project_id},
            cookies={"access_token": client_with_auth.test_token},
        )
        task_id = task_response.json()["id"]
        
        # Delete task
        response = client_with_auth.delete(
            f"/project/task/{task_id}",
            cookies={"access_token": client_with_auth.test_token},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == task_id

    def test_delete_task_not_found(self, client_with_auth):
        """Test deleting non-existent task returns 404."""
        fake_id = str(uuid.uuid4())
        
        response = client_with_auth.delete(
            f"/project/task/{fake_id}",
            cookies={"access_token": client_with_auth.test_token},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_task_no_auth(self, client_with_auth):
        """Test deleting task without auth returns 401."""
        fake_id = str(uuid.uuid4())
        
        response = client_with_auth.delete(f"/project/task/{fake_id}")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
