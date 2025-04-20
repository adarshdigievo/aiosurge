from io import StringIO
from unittest import mock
import pytest
import httpx

import aiosurge
from aiosurge.api_resource import APIResource
from aiosurge.errors import SurgeRequestError, SurgeMissingAPIKeyError


@pytest.mark.asyncio
async def test_raise_exception_if_missing_api_key():
    with pytest.raises(SurgeMissingAPIKeyError) as e_info:
        aiosurge.api_key = None
        await APIResource._base_request("get", aiosurge.api_resource.PROJECTS_ENDPOINT)


@pytest.mark.asyncio
async def test_raise_exception_if_invalid_http_method():
    with pytest.raises(SurgeRequestError) as e_info:
        aiosurge.api_key = "api-key"
        await APIResource._base_request("test", aiosurge.api_resource.PROJECTS_ENDPOINT)


@pytest.mark.asyncio
async def test_raise_exception_if_invalid_api_key():
    with pytest.raises(SurgeRequestError) as e_info:
        aiosurge.api_key = "api-key"
        await APIResource._base_request("get", aiosurge.api_resource.PROJECTS_ENDPOINT)


@pytest.mark.asyncio
async def test_passed_in_api_key():
    with mock.patch.object(httpx.AsyncClient, "get") as mock_request:
        mock_request.return_value = mock.MagicMock()
        await APIResource._base_request(
            "get", aiosurge.api_resource.PROJECTS_ENDPOINT, api_key="passed_api_key"
        )
        mock_request.assert_called_once_with(
            "https://app.surgehq.ai/api/projects",
            auth=("passed_api_key", ""),
            params=None,
        )


@pytest.mark.asyncio
async def test_passed_in_file():
    with mock.patch.object(httpx.AsyncClient, "post") as mock_request:
        files = {"file": StringIO()}
        mock_request.return_value = mock.MagicMock()
        await APIResource._base_request(
            "post",
            aiosurge.api_resource.PROJECTS_ENDPOINT,
            files=files,
            api_key="passed_api_key",
        )
        mock_request.assert_called_once_with(
            "https://app.surgehq.ai/api/projects",
            auth=("passed_api_key", ""),
            files=files,
            json=None,
        )


@pytest.mark.asyncio
async def test_get_passed_in_file():
    with pytest.raises(SurgeRequestError) as e_info:
        files = {"file": StringIO()}
        await APIResource._base_request(
            "get",
            aiosurge.api_resource.PROJECTS_ENDPOINT,
            files=files,
            api_key="passed_api_key",
        )


def test_print_attrs():
    a1 = APIResource(id="ABC1234").print_attrs()
    assert a1 == 'id="ABC1234"'
