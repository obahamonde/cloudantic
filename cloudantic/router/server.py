"""REST API Module with automatic OpenAPI generation."""
import asyncio
import os
from functools import wraps
from inspect import signature
from typing import Any, Awaitable, Callable, TypeVar, cast

from aiohttp.typedefs import Handler
from aiohttp.web import (Application, HTTPFound, Request, Response,
                         StreamResponse)
from aiohttp.web_middlewares import _Middleware as Middleware  # type: ignore
from aiohttp.web_middlewares import middleware
from aiohttp.web_ws import WebSocketResponse
from aiohttp_sse import EventSourceResponse, sse_response  # type: ignore
from typing_extensions import ParamSpec

from ..schema.json import jsonable_encoder
from ..schema.odm import DynaModel
from ..utils import setup_logging
from .api import APIRouter
from .docs import extract, html_string, load, transform
from .helpers import do_response

P = ParamSpec("P")
T = TypeVar("T")


class APIServer(Application):
    """Cloudantic APIServer"""

    def __init__(
        self,
        *args: Any,
        title: str = "Cloudantic",
        servers: list[str] | None = None,
        description: str = "Cloudantic API",
        version: str = "0.0.1",
        openapi_url: str = "/openapi.json",
        **kwargs: Any,
    ):
        super().__init__(*args, logger=setup_logging(self.__class__.__name__), **kwargs)
        schemas = DynaModel.__subclasses__()
        self.openapi: dict[str, Any] = {
            "openapi": "3.0.0",
            "info": {"title": title, "version": version},
            "paths": {},
            "tags": [],
            "components": {
                "schemas": {schema.__name__: schema.schema() for schema in schemas}
            },
            "description": description,
        }
        if servers:
            self.openapi["servers"] = servers
        self._route_open_api_params: dict[str, Any] = {}
        self.openapi_url = openapi_url

        @self.get("/openapi.json")
        async def _():
            response = jsonable_encoder(self.openapi)
            return response

        @self.get("/docs")
        async def _():
            return Response(
                text=html_string(self.openapi_url), content_type="text/html"
            )

    def document(
        self, path: str, method: str
    ) -> Callable[
        [Callable[P, Awaitable[StreamResponse]]], Callable[P, Awaitable[StreamResponse]]
    ]:
        """

        SWAGGER DOCUMENTATION

        """

        def decorator(func: Callable[P, Awaitable[T]]) -> Callable[P, Awaitable[T]]:
            sig = signature(func)
            params = sig.parameters
            open_api_params = extract(params.copy(), path)
            self._route_open_api_params[(path, method)] = open_api_params # type: ignore
            transform(self.openapi, path, method, func, open_api_params)

            async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
                request: Request = cast(Request, args[0])
                args_ = args[1:]
                args_to_apply = await load(request, params.copy())
                definitive_args = {}
                for name, param in params.items():
                    if name in args_to_apply:
                        definitive_args[name] = args_to_apply[name]
                    elif param.default is not param.empty:
                        definitive_args[name] = param.default
                    else:
                        raise ValueError(
                            f"Missing parameter {name} for {func.__name__}"
                        )
                if asyncio.iscoroutinefunction(func):
                    response = await func(*args_, **kwargs, **definitive_args) # type: ignore
                else:
                    response = func(*args_, **kwargs, **definitive_args) # type: ignore
                return cast(T, do_response(response))

            wrapper._handler = func  # type: ignore
            return wrapper

        return decorator

    def get( # type: ignore
        self, path: str, **kwargs: Any
    ) -> Callable[[Callable[P, Awaitable[T]]], Callable[P, Awaitable[T]]]:
        """GET decorator"""

        def decorator(func: Callable[P, Awaitable[T]]) -> Callable[P, Awaitable[T]]:
            self.router.add_get(path, self.document(path, "GET")(func),  **kwargs) # type: ignore
            return func

        return decorator

    def post(
        self, path: str, **kwargs: Any
    ) -> Callable[[Callable[P, Awaitable[T]]], Callable[P, Awaitable[T]]]:
        """POST decorator"""

        def decorator(func: Callable[P, Awaitable[T]]) -> Callable[P, Awaitable[T]]:
            self.router.add_post(path, self.document(path, "POST")(func), **kwargs) # type: ignore
            return func

        return decorator

    def put(
        self, path: str, **kwargs: Any
    ) -> Callable[[Callable[P, Awaitable[T]]], Callable[P, Awaitable[T]]]:
        """PUT decorator"""

        def decorator(func: Callable[P, Awaitable[T]]) -> Callable[P, Awaitable[T]]:
            self.router.add_put(path, self.document(path, "PUT")(func), **kwargs) # type: ignore
            return func

        return decorator

    def delete(
        self, path: str, **kwargs: Any
    ) -> Callable[[Callable[P, Awaitable[T]]], Callable[P, Awaitable[T]]]:
        """DELETE decorator"""

        def decorator(func: Callable[P, Awaitable[T]]) -> Callable[P, Awaitable[T]]:
            self.router.add_delete(path, self.document(path, "DELETE")(func), **kwargs) # type: ignore
            return func

        return decorator

    def patch(
        self, path: str, **kwargs: Any
    ) -> Callable[[Callable[P, Awaitable[T]]], Callable[P, Awaitable[T]]]:
        """PATCH decorator"""

        def decorator(func: Callable[P, Awaitable[T]]) -> Callable[P, Awaitable[T]]:
            self.router.add_patch(path, self.document(path, "PATCH")(func), **kwargs) # type: ignore
            return func

        return decorator

    def head(
        self, path: str, **kwargs: Any
    ) -> Callable[
        [Callable[P, Awaitable[StreamResponse]]], Callable[P, Awaitable[StreamResponse]]
    ]:
        """HEAD decorator"""

        def decorator(func: Callable[P, Awaitable[T]]) -> Callable[P, Awaitable[T]]:
            self.router.add_head(path, self.document(path, "HEAD")(func), **kwargs) # type: ignore
            return func

        return decorator

    def options(self, path: str, **kwargs:Any):
        """OPTIONS decorator"""

        def decorator(func: Callable[P, Awaitable[T]]) -> Callable[P, Awaitable[T]]:
            self.router.add_options(
                path, self.document(path, "OPTIONS")(func), **kwargs # type: ignore
            ) # type: ignore
            return func

        return decorator

    def on_event(
        self, event: str
    ) -> Callable[
        [Callable[[Application], Awaitable[None]]],
        Callable[[Application], Awaitable[None]],
    ]:
        """On event handler"""

        def decorator(
            func: Callable[[Application], Awaitable[None]]
        ) -> Callable[[Application], Awaitable[None]]:
            if event not in ("startup", "shutdown"):
                raise ValueError("Event must be startup or shutdown")
            elif event == "startup":
                self.on_startup.append(func)
            else:
                self.on_shutdown.append(func)
            return func

        return decorator

    def sse(
        self, path: str
    ) -> Callable[[Callable[P, Awaitable[T]]], Callable[P, Awaitable[T]],]:
        """Server Sent Events decorator"""

        def decorator(
            func: Callable[P, Awaitable[EventSourceResponse]]
        ) -> Callable[P, Awaitable[EventSourceResponse]]:
            @wraps(func)
            async def wrapper(request: Request) -> EventSourceResponse:
                async with sse_response(request) as resp: # type: ignore
                    args_to_apply = await load(
                        request, signature(func).parameters.copy()
                    )
                    definitive_args = {}
                    for name, param in signature(func).parameters.items():
                        if param.annotation == EventSourceResponse:
                            definitive_args[name] = resp # type: ignore
                        elif name in args_to_apply:
                            definitive_args[name] = args_to_apply[name]
                            args_to_apply.pop(name)
                        elif param.default is not param.empty:
                            definitive_args[name] = param.default
                        else:
                            raise ValueError(
                                f"Missing parameter {name} for {func.__name__}"
                            )
                    await func(**definitive_args) # type: ignore
                    return resp # type: ignore

            self.router.add_get(path, wrapper)
            return wrapper # type: ignore

        return decorator # type: ignore

    def websocket(
        self, path: str
    ) -> Callable[[Callable[P, Awaitable[T]]], Callable[P, Awaitable[T]],]:
        """Websocket decorator"""

        def decorator(
            func: Callable[P, Awaitable[WebSocketResponse]]
        ) -> Callable[P, Awaitable[WebSocketResponse]]:
            @wraps(func)
            async def wrapper(request: Request):
                args_to_apply = await load(request, signature(func).parameters.copy())
                ws = WebSocketResponse()
                await ws.prepare(request)
                definitive_args = {}
                for name, param in signature(func).parameters.items():
                    if param.annotation == WebSocketResponse:
                        definitive_args[name] = ws
                    elif name in args_to_apply:
                        definitive_args[name] = args_to_apply[name]
                        args_to_apply.pop(name)
                    elif param.default is not param.empty:
                        definitive_args[name] = param.default
                    else:
                        raise ValueError(
                            f"Missing parameter {name} for {func.__name__}"
                        )
                await func(**definitive_args) # type: ignore
                return ws

            self.router.add_get(path, wrapper)
            return wrapper # type: ignore

        return decorator # type: ignore

    def static(self) -> "APIServer":
        """Static folder creation and serving"""

        @self.get("/")
        async def _():
            return HTTPFound("/index.html")

        try:
            os.makedirs("static", exist_ok=True)
        except OSError:
            pass
        self.router.add_static("/", "static")

        return self

    def middleware(self, func: Middleware) -> Middleware:
        @wraps(func)
        @middleware
        async def wrapper(request: Request, handler: Handler) -> Response:
            response = await func(request, handler)
            if isinstance(response, Response):
                return response
            return do_response(response)

        self.middlewares.append(wrapper)
        return wrapper

    def use(self, router: APIRouter, prefix: str = "") -> "APIServer":
        """Chainable method to add a router to the server"""
        for route in router.routes:
            path = prefix + route.path
            self.router.add_route(
                route.method,
                prefix + router.prefix + path,
                route.handler,
                **route.kwargs,
            )

        for path, details in router.openapi["paths"].items():
            path = prefix + path
            self.openapi["paths"][path] = details

        self.openapi["components"]["schemas"].update(
            router.openapi["components"]["schemas"]
        )
        return self
