import pytest
from fastapi import status
import uuid


class TestCreateClientEndpoint:
    """Test POST /client/ endpoint."""

    def test_create_client_success(self, client_with_auth):
        """Test successful client creation."""
        response = client_with_auth.post(
            "/client/",
            json={"name": "Acme Corp", "notes": "A great company"},
            cookies={"access_token": client_with_auth.test_token},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Acme Corp"
        assert data["notes"] == "A great company"
        assert "id" in data
        assert data["user_id"] == str(client_with_auth.test_user.id)

    def test_create_client_without_notes(self, client_with_auth):
        """Test creating client without optional notes."""
        response = client_with_auth.post(
            "/client/",
            json={"name": "Simple Corp"},
            cookies={"access_token": client_with_auth.test_token},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Simple Corp"
        assert data["notes"] is None

    def test_create_client_with_rate(self, client_with_auth):
        """Test creating client with rate."""
        response = client_with_auth.post(
            "/client/",
            json={"name": "Rate Corp", "rate": 150.50},
            cookies={"access_token": client_with_auth.test_token},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Rate Corp"
        assert data["rate"] == 150.50

    def test_create_client_missing_name(self, client_with_auth):
        """Test that missing name returns 422."""
        response = client_with_auth.post(
            "/client/",
            json={"notes": "Missing name"},
            cookies={"access_token": client_with_auth.test_token},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_client_no_auth(self, client_with_auth):
        """Test that creating client without auth returns 401."""
        response = client_with_auth.post(
            "/client/",
            json={"name": "Unauthorized Corp"},
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestGetClientEndpoint:
    """Test GET /client/get/{client_id} endpoint."""

    def test_get_client_success(self, client_with_auth):
        """Test successfully retrieving a client."""
        # Create a client first
        create_response = client_with_auth.post(
            "/client/",
            json={"name": "Test Client", "notes": "Test notes"},
            cookies={"access_token": client_with_auth.test_token},
        )
        client_id = create_response.json()["id"]
        
        # Get the client
        response = client_with_auth.get(
            f"/client/get/{client_id}",
            cookies={"access_token": client_with_auth.test_token},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Test Client"
        assert data["id"] == client_id

    def test_get_client_not_found(self, client_with_auth):
        """Test getting non-existent client returns 404."""
        fake_id = str(uuid.uuid4())
        
        response = client_with_auth.get(
            f"/client/get/{fake_id}",
            cookies={"access_token": client_with_auth.test_token},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"].lower()

    def test_get_client_wrong_user(self, client_with_auth):
        """Test that user can't access another user's client with invalid token."""
        # Create a client with user1
        create_response = client_with_auth.post(
            "/client/",
            json={"name": "User1 Client"},
            cookies={"access_token": client_with_auth.test_token},
        )
        client_id = create_response.json()["id"]
        
        # Try to access with invalid token (different user)
        # Using a bogus token that won't validate
        response = client_with_auth.get(
            f"/client/get/{client_id}",
            cookies={"access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U"},
        )

        # Should get 401 since token is invalid
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestListClientsEndpoint:
    """Test GET /client/all/ endpoint."""

    def test_list_clients_success(self, client_with_auth):
        """Test listing all clients for a user."""
        # Create multiple clients
        client_with_auth.post(
            "/client/",
            json={"name": "Client 1"},
            cookies={"access_token": client_with_auth.test_token},
        )
        client_with_auth.post(
            "/client/",
            json={"name": "Client 2"},
            cookies={"access_token": client_with_auth.test_token},
        )
        
        # List all clients
        response = client_with_auth.get(
            "/client/all/",
            cookies={"access_token": client_with_auth.test_token},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 2
        assert data[0]["name"] == "Client 1"
        assert data[1]["name"] == "Client 2"

    def test_list_clients_empty(self, client_with_auth):
        """Test listing clients when user has none."""
        response = client_with_auth.get(
            "/client/all/",
            cookies={"access_token": client_with_auth.test_token},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 0

    def test_list_clients_no_auth(self, client_with_auth):
        """Test that listing without auth returns 401."""
        response = client_with_auth.get("/client/all/")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestUpdateClientEndpoint:
    """Test PATCH /client/{client_id} endpoint."""

    def test_update_client_name(self, client_with_auth):
        """Test updating client name."""
        # Create a client
        create_response = client_with_auth.post(
            "/client/",
            json={"name": "Old Name"},
            cookies={"access_token": client_with_auth.test_token},
        )
        client_id = create_response.json()["id"]
        
        # Update it
        response = client_with_auth.patch(
            f"/client/{client_id}",
            json={"name": "New Name"},
            cookies={"access_token": client_with_auth.test_token},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "New Name"

    def test_update_client_notes(self, client_with_auth):
        """Test updating client notes."""
        # Create a client
        create_response = client_with_auth.post(
            "/client/",
            json={"name": "Test Client"},
            cookies={"access_token": client_with_auth.test_token},
        )
        client_id = create_response.json()["id"]
        
        # Update notes
        response = client_with_auth.patch(
            f"/client/{client_id}",
            json={"notes": "Updated notes"},
            cookies={"access_token": client_with_auth.test_token},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["notes"] == "Updated notes"

    def test_update_client_partial(self, client_with_auth):
        """Test partial update (only update one field)."""
        # Create a client
        create_response = client_with_auth.post(
            "/client/",
            json={"name": "Original", "notes": "Original notes"},
            cookies={"access_token": client_with_auth.test_token},
        )
        client_id = create_response.json()["id"]
        
        # Update only name
        response = client_with_auth.patch(
            f"/client/{client_id}",
            json={"name": "Updated Name"},
            cookies={"access_token": client_with_auth.test_token},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["notes"] == "Original notes"  # Should not change

    def test_update_client_not_found(self, client_with_auth):
        """Test updating non-existent client returns 404."""
        fake_id = str(uuid.uuid4())
        
        response = client_with_auth.patch(
            f"/client/{fake_id}",
            json={"name": "New Name"},
            cookies={"access_token": client_with_auth.test_token},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestDeleteClientEndpoint:
    """Test DELETE /client/{client_id} endpoint."""

    def test_delete_client_success(self, client_with_auth):
        """Test successfully deleting a client."""
        # Create a client
        create_response = client_with_auth.post(
            "/client/",
            json={"name": "Client to Delete"},
            cookies={"access_token": client_with_auth.test_token},
        )
        client_id = create_response.json()["id"]
        
        # Delete it
        response = client_with_auth.delete(
            f"/client/{client_id}",
            cookies={"access_token": client_with_auth.test_token},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == client_id
        
        # Verify it's gone
        get_response = client_with_auth.get(
            f"/client/get/{client_id}",
            cookies={"access_token": client_with_auth.test_token},
        )
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_client_not_found(self, client_with_auth):
        """Test deleting non-existent client returns 404."""
        fake_id = str(uuid.uuid4())
        
        response = client_with_auth.delete(
            f"/client/{fake_id}",
            cookies={"access_token": client_with_auth.test_token},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_client_no_auth(self, client_with_auth):
        """Test deleting client without auth returns 401."""
        fake_id = str(uuid.uuid4())
        
        response = client_with_auth.delete(f"/client/{fake_id}")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    def test_delete_client_preserves_projects(self, client_with_auth):
        """Test that deleting a client sets projects' client_id to None instead of cascade deleting."""
        # Create a client
        client_response = client_with_auth.post(
            "/client/",
            json={"name": "Client with Projects"},
            cookies={"access_token": client_with_auth.test_token},
        )
        client_id = client_response.json()["id"]
        
        # Create a project with this client
        project_response = client_with_auth.post(
            "/project/",
            json={"name": "Test Project", "client_id": client_id},
            cookies={"access_token": client_with_auth.test_token},
        )
        project_id = project_response.json()["id"]
        
        # Verify project has the client
        get_project_response = client_with_auth.get(
            f"/project/get/{project_id}",
            cookies={"access_token": client_with_auth.test_token},
        )
        assert get_project_response.json()["client_id"] == client_id
        
        # Delete the client
        delete_response = client_with_auth.delete(
            f"/client/{client_id}",
            cookies={"access_token": client_with_auth.test_token},
        )
        assert delete_response.status_code == status.HTTP_200_OK
        
        # Verify project still exists but client_id is None
        get_project_response = client_with_auth.get(
            f"/project/get/{project_id}",
            cookies={"access_token": client_with_auth.test_token},
        )
        assert get_project_response.status_code == status.HTTP_200_OK
        assert get_project_response.json()["client_id"] is None