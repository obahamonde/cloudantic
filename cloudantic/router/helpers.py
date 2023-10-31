"""
Helper functions for Cloudantic.
"""
from functools import singledispatch
from typing import Any, List, Union

from aiohttp.web import Response, json_response
from pydantic import BaseModel  # pylint: disable=no-name-in-module

from ..schema.json import *
from ..schema.odm import DynaModel


@singledispatch
def do_response(response: Any) -> Response:
    """
    Process the response from a view function and return an aiohttp.web.Response object.
    """

    return response


@do_response.register(BaseModel)
def _(response: BaseModel) -> Response:
    return json_response(response.dict(exclude_none=True), dumps=to_json)


@do_response.register(DynaModel)
def _(response: DynaModel) -> Response:
    return json_response(response.dict(), dumps=to_json)


@do_response.register(dict)
def _(response: dict[str,Any]) -> Response:
    return json_response(response, dumps=to_json)


@do_response.register(str)
def _(response: str) -> Response:
    return Response(status=200, text=response, content_type="text/html")


@do_response.register(bytes)
def _(response: bytes) -> Response:
    return Response(
        status=200, body=response, content_type="application/octet-sse_stream"
    )


@do_response.register(int)
def _(response: int) -> Response:
    return Response(status=200, text=str(response), content_type="text/plain")


@do_response.register(float)
def _(response: float) -> Response:
    return Response(status=200, text=str(response), content_type="text/plain")


@do_response.register(bool)
def _(response: bool) -> Response:
    return Response(status=200, text=str(response), content_type="text/plain")


@do_response.register(list)
def _(response: List[Union[DynaModel, BaseModel, dict[str,Any], str, int, float]]) -> Response:
    return json_response(response, dumps=to_json)


@do_response.register(tuple)
def _(response: tuple[Any]) -> Response:
    return do_response(list(response))


@do_response.register(set)
def _(response: set[Any]) -> Response:
    return do_response(list(response))


@do_response.register(frozenset)
def _(response: frozenset[Any]) -> Response:
    return do_response(list(response))


@do_response.register(type(None))
def _(response: None) -> Response:
    return Response(status=200, text="", content_type="text/plain")


@do_response.register(Response)
def _(response: Response) -> Response:
    return response
