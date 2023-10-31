from typing import Any, Optional

import aiohttp
from pydantic import BaseModel, Field  # pylint: disable=no-name-in-module

from ..utils import retry, setup_logging

logger = setup_logging(__name__)


class APIClient(BaseModel):
    """
    A class representing an API client.

    Attributes:
    -----------
    headers : dict
        The headers to be used for the API requests.
    base_url : strÍ
        The base URL for the API requests.
    """

    base_url: str = Field(..., description="The base URL for the API requests")
    headers: dict[str, str] = Field(
        ..., description="The headers to be used for the API requests"
    )

    @retry()
    async def get(
        self,
        endpoint: str,
        params: Optional[dict[str, Any]] = None,
        session: Optional[aiohttp.ClientSession] = None,
    ):
        """
        Sends a GET request to the API.

        Parameters:
        -----------
        endpoint : str
            The endpoint to send the request to.
        params : Optional[dict[str, Any]]
            The query parameters to be used for the request.

        Returns:
        --------
        dict
            The response from the API.
        """
        if session is not None:
            try:
                response = await session.get(endpoint, params=params)
                data = await response.json()
                logger.info("GET %s %s %s", endpoint, response.status, data)
                return data
            except Exception as e:
                logger.error("GET %s %s", endpoint, e)
                raise e
        else:
            try:
                async with aiohttp.ClientSession(
                    base_url=self.base_url, headers=self.headers
                ) as session:
                    response = await session.get(endpoint, params=params)
                    data = await response.json()
                    logger.info("GET %s %s %s", endpoint, response.status, data)
                    return data
            except Exception as e:
                logger.error("GET %s %s", endpoint, e)
                raise e

    @retry()
    async def post(
        self,
        endpoint: str,
        data: Optional[dict[str, Any]] = None,
        session: Optional[aiohttp.ClientSession] = None,
    ):
        """
        Sends a POST request to the API.

        Parameters:
        -----------
        endpoint : str
            The endpoint to send the request to.
        data : Optional[dict[str, Any]]
            The data to be sent with the request.

        Returns:
        --------
        dict
            The response from the API.
        """
        if session is not None:
            try:
                response = await session.post(endpoint, json=data)
                data = await response.json()
                logger.info("POST %s %s %s", endpoint, response.status, data)
                return data
            except Exception as e:
                logger.error("POST %s %s", endpoint, e)
                raise e
        else:
            try:
                async with aiohttp.ClientSession(
                    base_url=self.base_url, headers=self.headers
                ) as session:
                    response = await session.post(endpoint, json=data)
                    data = await response.json()
                    logger.info("POST %s %s %s", endpoint, response.status, data)
                    return data
            except Exception as e:
                logger.error("POST %s %s", endpoint, e)
                raise e

    @retry()
    async def put(
        self,
        endpoint: str,
        data: Optional[dict[str, Any]] = None,
        session: Optional[aiohttp.ClientSession] = None,
    ):
        """
        Sends a PUT request to the API.

        Parameters:
        -----------
        endpoint : str
            The endpoint to send the request to.
        data : Optional[dict[str, Any]]
            The data to be sent with the request.

        Returns:
        --------
        dict
            The response from the API.
        """
        if session is not None:
            try:
                response = await session.put(endpoint, json=data)
                data = await response.json()
                logger.info("PUT %s %s %s", endpoint, response.status, data)
                return data
            except Exception as e:
                logger.error("PUT %s %s", endpoint, e)
                raise e
        else:
            try:
                async with aiohttp.ClientSession(
                    base_url=self.base_url, headers=self.headers
                ) as session:
                    response = await session.put(endpoint, json=data)
                    data = await response.json()
                    logger.info("PUT %s %s %s", endpoint, response.status, data)
                    return data
            except Exception as e:
                logger.error("PUT %s %s", endpoint, e)
                raise e

    @retry()
    async def delete(
        self,
        endpoint: str,
        params: Optional[dict[str, Any]] = None,
        session: Optional[aiohttp.ClientSession] = None,
    ):
        """
        Sends a DELETE request to the API.

        Parameters:
        -----------
        endpoint : str
            The endpoint to send the request to.

        Returns:
        --------
        dict
            The response from the API.
        """
        if session is not None:
            try:
                response = await session.delete(endpoint, params=params)
                data = await response.json()
                logger.info("DELETE %s %s %s", endpoint, response.status, data)
                return data
            except Exception as e:
                logger.error("DELETE %s %s", endpoint, e)
                raise e
        else:
            async with aiohttp.ClientSession(
                base_url=self.base_url, headers=self.headers
            ) as session:
                try:
                    response = await session.delete(endpoint, params=params)
                    data = await response.json()
                    logger.info("DELETE %s %s %s", endpoint, response.status, data)
                    return data
                except Exception as e:
                    logger.error("DELETE %s %s", endpoint, e)
                    raise e

    @retry()
    async def patch(
        self,
        endpoint: str,
        data: Optional[dict[str, Any]] = None,
        session: Optional[aiohttp.ClientSession] = None,
    ):
        """
        Sends a PATCH request to the API.
        """
        if session is not None:
            try:
                response = await session.patch(endpoint, json=data)
                data = await response.json()
                logger.info("PATCH %s %s %s", endpoint, response.status, data)
                return data
            except Exception as e:
                logger.error("PATCH %s %s", endpoint, e)
                raise e
        else:
            async with aiohttp.ClientSession(
                base_url=self.base_url, headers=self.headers
            ) as session:
                try:
                    response = await session.patch(endpoint, json=data)
                    data = await response.json()
                    logger.info("PATCH %s %s %s", endpoint, response.status, data)
                    return data
                except Exception as e:
                    logger.error("PATCH %s %s", endpoint, e)
                    raise e

    @retry()
    async def head(
        self, endpoint: str, session: Optional[aiohttp.ClientSession] = None
    ):
        """
        Sends a HEAD request to the API.

        Parameters:
        -----------
        endpoint : str
            The endpoint to send the request to.

        Returns:
        --------
        dict
            The response from the API.
        """
        if session is not None:
            try:
                response = await session.head(endpoint)
                data = await response.json()
                logger.info("HEAD %s %s %s", endpoint, response.status, data)
                return data
            except Exception as e:
                logger.error("HEAD %s %s", endpoint, e)
                raise e
        else:
            async with aiohttp.ClientSession(
                base_url=self.base_url, headers=self.headers
            ) as session:
                try:
                    response = await session.head(endpoint)
                    data = await response.json()
                    logger.info("HEAD %s %s %s", endpoint, response.status, data)
                    return data
                except Exception as e:
                    logger.error("HEAD %s %s", endpoint, e)
                    raise e

    @retry()
    async def options(
        self, endpoint: str, session: Optional[aiohttp.ClientSession] = None
    ):
        """
        Sends an OPTIONS request to the API.

        Parameters:
        -----------
        endpoint : str
            The endpoint to send the request to.

        Returns:
        --------
        dict
            The response from the API.
        """
        if session is not None:
            try:
                response = await session.options(endpoint)
                data = await response.json()
                logger.info(f"OPTIONS {endpoint} {response.status} {data}")
                return data
            except Exception as e:
                logger.error("OPTIONS %s %s", endpoint, e)
                raise e
        else:
            async with aiohttp.ClientSession(
                base_url=self.base_url, headers=self.headers
            ) as session:
                try:
                    response = await session.options(endpoint)
                    data = await response.json()
                    logger.info(f"OPTIONS {endpoint} {response.status} {data}")
                    return data
                except Exception as e:
                    logger.error("OPTIONS %s %s", endpoint, e)
                    raise e

    @retry()
    async def text(
        self,
        endpoint: str,
        params: Optional[dict[str, Any]] = None,
        session: Optional[aiohttp.ClientSession] = None,
    ):
        """
        Sends a GET request to the API and returns the response as text.

        Parameters:
        -----------
        endpoint : str
            The endpoint to send the request to.

        Returns:
        --------
        str
            The response from the API.
        """
        if session is not None:
            try:
                response = await session.get(endpoint, params=params)
                data = response.text
                logger.info(f"GET {endpoint} {response.status} {data}")
                return data
            except Exception as e:
                logger.error(f"GET {endpoint} {e}")
                raise e
        else:
            async with aiohttp.ClientSession(
                base_url=self.base_url, headers=self.headers
            ) as session:
                try:
                    response = await session.get(endpoint, params=params)
                    data = response.text
                    logger.info(f"GET {endpoint} {response.status} {data}")
                    return data
                except Exception as e:
                    logger.error(f"GET {endpoint} {e}")
                    raise e

    @retry()
    async def blob(
        self,
        endpoint: str,
        params: Optional[dict[str, Any]] = None,
        session: Optional[aiohttp.ClientSession] = None,
    ):
        """
        Sends a GET request to the API and returns the response as bytes.

        Parameters:
        -----------
        endpoint : str
            The endpoint to send the request to.

        Returns:
        --------
        bytes
            The response from the API.
        """
        if session is not None:
            try:
                response = await session.get(endpoint, params=params)
                data = response.content
                logger.info(f"GET {endpoint} {response.status} {data}")
                return data
            except Exception as e:
                logger.error(f"GET {endpoint} {e}")
                raise e
        else:
            async with aiohttp.ClientSession(
                base_url=self.base_url, headers=self.headers
            ) as session:
                try:
                    response = await session.get(endpoint, params=params)
                    data = response.content
                    logger.info(f"GET {endpoint} {response.status} {data}")
                    return data
                except Exception as e:
                    logger.error(f"GET {endpoint} {e}")
                    raise e

    async def stream(
        self,
        endpoint: str,
        params: Optional[dict[str, Any]],
        session: Optional[aiohttp.ClientSession] = None,
    ):
        """
        Sends a GET request to the API and returns the response as a stream.

        Parameters:
        -----------
        endpoint : str
            The endpoint to send the request to.

        Returns:
        --------
        httpx.Response
            The response from the API.
        """
        if session is not None:
            try:
                async with session.request("GET", endpoint, params=params) as response:
                    async for chunk in response.content.iter_any():
                        yield chunk
            except Exception as e:
                logger.error(f"GET {endpoint} {e}")
                raise e
        else:
            async with aiohttp.ClientSession(
                base_url=self.base_url, headers=self.headers
            ) as session:
                try:
                    async with session.request(
                        "GET", endpoint, params=params
                    ) as response:
                        async for chunk in response.content.iter_any():
                            yield chunk
                except Exception as e:
                    logger.error(f"GET {endpoint} {e}")
                    raise e
