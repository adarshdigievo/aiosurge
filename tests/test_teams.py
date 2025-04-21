import base64
import json
from datetime import datetime
import pytest
from pytest_httpx import HTTPXMock

import aiosurge
from aiosurge.teams import Team
from aiosurge.api_resource import TEAMS_ENDPOINT
from aiosurge.errors import SurgeMissingIDError


@pytest.fixture
def mock_team_data():
    return {
        "id": "team123",
        "name": "Test Team",
        "description": "A team for testing",
        "created_at": "2025-04-21T10:15:02Z",
        "members": ["user1", "user2"],
    }


@pytest.fixture
def mock_teams_list():
    return [
        {
            "id": "team123",
            "name": "Test Team 1",
            "description": "A team for testing",
            "created_at": "2025-04-21T10:15:02Z",
            "members": ["user1", "user2"],
        },
        {
            "id": "team456",
            "name": "Test Team 2",
            "description": "Another team for testing",
            "created_at": "2025-04-21T11:15:02Z",
            "members": ["user3", "user4"],
        },
    ]


@pytest.fixture
def setup_api_key():
    # Set API key for tests
    aiosurge.api_key = "test-api-key"
    yield
    # Clean up after tests
    aiosurge.api_key = None


class TestTeam:
    def test_init_missing_id(self):
        with pytest.raises(SurgeMissingIDError):
            Team()

    def test_init_with_data(self, mock_team_data):
        team = Team(**mock_team_data)
        assert team.id == "team123"
        assert team.name == "Test Team"
        assert team.description == "A team for testing"
        assert isinstance(team.created_at, datetime)
        assert team.members == ["user1", "user2"]

    def test_str_representation(self, mock_team_data):
        team = Team(**mock_team_data)
        assert str(team) == "<surge.Team#team123>"

    def test_repr_representation(self, mock_team_data):
        team = Team(**mock_team_data)
        assert 'name="Test Team"' in repr(team)
        assert 'description="A team for testing"' in repr(team)


@pytest.mark.asyncio
class TestTeamAsyncMethods:
    async def test_create(self, httpx_mock: HTTPXMock, setup_api_key, mock_team_data):
        # Configure mock
        httpx_mock.add_response(
            method="POST",
            url=f"{aiosurge.base_url}/{TEAMS_ENDPOINT}",
            json=mock_team_data,
            status_code=200,
        )

        # Test Team.create
        team = await Team.create(
            name="Test Team",
            members=["user1", "user2"],
            description="A team for testing",
        )

        # Verify request was made correctly
        request = httpx_mock.get_request()
        assert request.url == f"{aiosurge.base_url}/{TEAMS_ENDPOINT}"
        assert request.method == "POST"

        # Verify request body
        request_body = json.loads(request.content)
        assert request_body["name"] == "Test Team"
        assert request_body["members"] == ["user1", "user2"]
        assert request_body["description"] == "A team for testing"

        # Verify response
        assert team.id == "team123"
        assert team.name == "Test Team"
        assert team.description == "A team for testing"
        assert isinstance(team.created_at, datetime)

    async def test_list(self, httpx_mock: HTTPXMock, setup_api_key, mock_teams_list):
        # Configure mock
        httpx_mock.add_response(
            method="GET",
            url=f"{aiosurge.base_url}/{TEAMS_ENDPOINT}/list",
            json=mock_teams_list,
            status_code=200,
        )

        # Test Team.list
        teams = await Team.list()

        # Verify request was made correctly
        request = httpx_mock.get_request()
        assert request.url == f"{aiosurge.base_url}/{TEAMS_ENDPOINT}/list"
        assert request.method == "GET"

        # Verify response
        assert len(teams) == 2
        assert teams[0].id == "team123"
        assert teams[0].name == "Test Team 1"
        assert teams[1].id == "team456"
        assert teams[1].name == "Test Team 2"
        assert isinstance(teams[0].created_at, datetime)

    async def test_retrieve(self, httpx_mock: HTTPXMock, setup_api_key, mock_team_data):
        team_id = "team123"

        # Configure mock
        httpx_mock.add_response(
            method="GET",
            url=f"{aiosurge.base_url}/{TEAMS_ENDPOINT}/{team_id}",
            json=mock_team_data,
            status_code=200,
        )

        # Test Team.retrieve
        team = await Team.retrieve(team_id)

        # Verify request was made correctly
        request = httpx_mock.get_request()
        assert request.url == f"{aiosurge.base_url}/{TEAMS_ENDPOINT}/{team_id}"
        assert request.method == "GET"

        # Verify response
        assert team.id == "team123"
        assert team.name == "Test Team"
        assert team.description == "A team for testing"
        assert isinstance(team.created_at, datetime)

    async def test_delete(self, httpx_mock: HTTPXMock, setup_api_key):
        team_id = "team123"
        success_response = {"success": True}

        # Configure mock
        httpx_mock.add_response(
            method="DELETE",
            url=f"{aiosurge.base_url}/{TEAMS_ENDPOINT}/{team_id}",
            json=success_response,
            status_code=200,
        )

        # Test Team.delete
        response = await Team.delete(team_id)

        # Verify request was made correctly
        request = httpx_mock.get_request()
        assert request.url == f"{aiosurge.base_url}/{TEAMS_ENDPOINT}/{team_id}"
        assert request.method == "DELETE"

        # Verify response
        assert response == success_response
        assert response["success"] is True

    async def test_update(self, httpx_mock: HTTPXMock, setup_api_key, mock_team_data):
        updated_team_data = mock_team_data.copy()
        updated_team_data["name"] = "Updated Team Name"
        updated_team_data["description"] = "Updated description"

        # Create team instance
        team = Team(**mock_team_data)

        # Configure mock
        httpx_mock.add_response(
            method="PUT",
            url=f"{aiosurge.base_url}/{TEAMS_ENDPOINT}/{team.id}",
            json=updated_team_data,
            status_code=200,
        )

        # Test team.update
        updated_team = await team.update(
            name="Updated Team Name", description="Updated description"
        )

        # Verify request was made correctly
        request = httpx_mock.get_request()
        assert request.url == f"{aiosurge.base_url}/{TEAMS_ENDPOINT}/{team.id}"
        assert request.method == "PUT"

        # Verify request body
        request_body = json.loads(request.content)
        assert request_body["name"] == "Updated Team Name"
        assert request_body["description"] == "Updated description"

        # Verify response
        assert updated_team.id == team.id
        assert updated_team.name == "Updated Team Name"
        assert updated_team.description == "Updated description"

    async def test_add_surgers(
        self, httpx_mock: HTTPXMock, setup_api_key, mock_team_data
    ):
        # Create team instance
        team = Team(**mock_team_data)

        # New surgers to add
        surger_ids = ["user3", "user4"]

        # Updated team data with new surgers
        updated_team_data = mock_team_data.copy()
        updated_team_data["members"] = ["user1", "user2", "user3", "user4"]

        # Configure mock
        httpx_mock.add_response(
            method="POST",
            url=f"{aiosurge.base_url}/{TEAMS_ENDPOINT}/{team.id}/add_surgers",
            json=updated_team_data,
            status_code=200,
        )

        # Test team.add_surgers
        updated_team = await team.add_surgers(surger_ids)

        # Verify request was made correctly
        request = httpx_mock.get_request()
        assert (
            request.url == f"{aiosurge.base_url}/{TEAMS_ENDPOINT}/{team.id}/add_surgers"
        )
        assert request.method == "POST"

        # Verify request body
        request_body = json.loads(request.content)
        assert request_body["surger_ids"] == ["user3", "user4"]

        # Verify response
        assert updated_team.id == team.id
        assert updated_team.members == ["user1", "user2", "user3", "user4"]

    async def test_remove_surgers(
        self, httpx_mock: HTTPXMock, setup_api_key, mock_team_data
    ):
        # Create team instance
        team = Team(**mock_team_data)

        # Surgers to remove
        surger_ids = ["user2"]

        # Updated team data without removed surgers
        updated_team_data = mock_team_data.copy()
        updated_team_data["members"] = ["user1"]

        # Configure mock
        httpx_mock.add_response(
            method="POST",
            url=f"{aiosurge.base_url}/{TEAMS_ENDPOINT}/{team.id}/remove_surgers",
            json=updated_team_data,
            status_code=200,
        )

        # Test team.remove_surgers
        updated_team = await team.remove_surgers(surger_ids)

        # Verify request was made correctly
        request = httpx_mock.get_request()
        assert (
            request.url
            == f"{aiosurge.base_url}/{TEAMS_ENDPOINT}/{team.id}/remove_surgers"
        )
        assert request.method == "POST"

        # Verify request body
        request_body = json.loads(request.content)
        assert request_body["surger_ids"] == ["user2"]

        # Verify response
        assert updated_team.id == team.id
        assert updated_team.members == ["user1"]

    async def test_custom_api_key(
        self, httpx_mock: HTTPXMock, setup_api_key, mock_team_data
    ):
        custom_api_key = "custom-api-key"
        team_id = "team123"

        # Configure mock
        httpx_mock.add_response(
            method="GET",
            url=f"{aiosurge.base_url}/{TEAMS_ENDPOINT}/{team_id}",
            json=mock_team_data,
            status_code=200,
        )

        # Test Team.retrieve with custom API key
        team = await Team.retrieve(team_id, api_key=custom_api_key)

        # Verify request was made with custom API key
        request = httpx_mock.get_request()
        auth_header = request.headers.get("authorization")
        assert "Basic" in auth_header
        assert (
            base64.b64decode(auth_header.lstrip("Basic ")).decode("utf-8")
            == f"{custom_api_key}:"
        )

        # Verify response
        assert team.id == "team123"
