from typing import Optional

import httpx

import aiosurge
from aiosurge.errors import SurgeRequestError, SurgeMissingAPIKeyError

PROJECTS_ENDPOINT = "projects"
TASKS_ENDPOINT = "tasks"
REPORTS_ENDPOINT = "projects"
QUESTIONS_ENDPOINT = "items"
TEAMS_ENDPOINT = "teams"


class APIResource:
    _httpx_async_client: Optional[httpx.AsyncClient] = None

    def __init__(self, id=None):
        self.id = id

    def print_attrs(self, forbid_list: list = []):
        return " ".join(
            [f'{k}="{v}"' for k, v in self.__dict__.items() if not k in forbid_list]
        )

    @classmethod
    async def _base_request(
        cls, method, api_endpoint, params=None, files=None, api_key=None
    ):

        api_key_to_use = api_key or aiosurge.api_key
        if api_key_to_use is None:
            raise SurgeMissingAPIKeyError

        if files is not None and method != "post":
            raise SurgeRequestError("Can only upload files to a POST request")

        if not cls._httpx_async_client:
            cls._httpx_async_client = httpx.AsyncClient()

        try:
            url = f"{aiosurge.base_url}/{api_endpoint}"

            # GET request
            if method == "get":
                response = await cls._httpx_async_client.get(
                    url, auth=(api_key_to_use, ""), params=params
                )

            # POST request
            elif method == "post":
                if files is not None:
                    response = await cls._httpx_async_client.post(
                        url, auth=(api_key_to_use, ""), files=files, json=params
                    )
                else:
                    response = await cls._httpx_async_client.post(
                        url, auth=(api_key_to_use, ""), json=params
                    )

            # PUT request
            elif method == "put":
                if params is not None and len(params):
                    response = await cls._httpx_async_client.put(
                        url, auth=(api_key_to_use, ""), json=params
                    )
                else:
                    response = await cls._httpx_async_client.put(
                        url, auth=(api_key_to_use, "")
                    )

            elif method == "delete":
                response = await cls._httpx_async_client.delete(
                    url, auth=(api_key_to_use, "")
                )

            else:
                raise SurgeRequestError("Invalid HTTP method.")

            # Raise exception if there is an http error
            response.raise_for_status()

            # If no errors, return response as json
            return response.json()

        except httpx.HTTPError as err:
            message = err.args[0]
            message = f"{message}. {err.response.text}"
            raise SurgeRequestError(message) from None

        except httpx.DecodingError as err:
            message = err.args[0]
            raise SurgeRequestError(message) from None

        except Exception as err:
            # Generic exception handling
            raise SurgeRequestError

    @classmethod
    async def get(cls, api_endpoint, params=None, api_key=None):
        method = "get"
        return await cls._base_request(
            method, api_endpoint, params=params, api_key=api_key
        )

    @classmethod
    async def post(cls, api_endpoint, params=None, api_key=None, files=None):
        method = "post"
        return await cls._base_request(
            method, api_endpoint, params=params, api_key=api_key, files=files
        )

    @classmethod
    async def put(cls, api_endpoint, params=None, api_key=None):
        method = "put"
        return await cls._base_request(
            method, api_endpoint, params=params, api_key=api_key
        )

    @classmethod
    async def delete_request(cls, api_endpoint, api_key=None):
        method = "delete"
        return await cls._base_request(method, api_endpoint, api_key=api_key)
