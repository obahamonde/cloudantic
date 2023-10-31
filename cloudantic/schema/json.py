"""JSON utilities for Cloudantic."""
import base64
from datetime import date, datetime, time
from decimal import Decimal
from enum import Enum
from json import JSONEncoder
from typing import Any, Dict
from uuid import UUID

from pydantic import BaseModel


class CloudEncoder(JSONEncoder):
    """
    Encoder for:
    -----------
    - datetime.datetime
    - uuid.UUID
    - float
    """

    def default(self, o: Any):
        if isinstance(o, datetime):
            return o.isoformat()
        if isinstance(o, UUID):
            return str(o)
        if isinstance(o, float):
            return Decimal(str(o))
        if isinstance(o, BaseModel):
            return o.dict()
        return super().default(o)


def parse_json_hook(dct: Dict[str, Any]):
    for k, v in dct.items():
        if isinstance(v, float):
            dct[k] = Decimal(str(v))

    return dct


def to_json(data: Any) -> str:
    """
    Convert data to JSON.
    """
    return CloudEncoder().encode(data)


def jsonable_encoder(
    obj: Any,
    *,
    include: list[str] = [],
    exclude: list[str] = [],
    by_alias: bool = False,
    skip_defaults: bool = False,
    custom_encoder: Any = None,
) -> Any:
    """
    Convert any object to a JSON-serializable object.

    This function is used by Cloudantic to convert objects to JSON-serializable objects.

    It supports all the types supported by the standard json library, plus:

    * datetime.datetime
    * datetime.date
    * datetime.time
    * uuid.UUID
    * enum.Enum
    * pydantic.BaseModel
    """

    if custom_encoder is None:
        custom_encoder = CloudEncoder

    if obj is str:
        return "string"
    if obj is int or obj is float:
        return "integer"
    if obj is bool:
        return "boolean"
    if obj is None:
        return "null"
    if obj is list:
        return "array"
    if obj is dict:
        return "object"
    if obj is bytes:
        return "binary"
    if obj is datetime:
        return "date-time"
    if obj is date:
        return "date"
    if obj is time:
        return "time"
    if obj is UUID:
        return "uuid"
    if obj is Enum:
        return "enum"
    if isinstance(obj, (str, int, float, bool, type(None))):
        return obj
    if isinstance(obj, (list, tuple, set, frozenset)):
        return [
            jsonable_encoder(
                v,
                include=include,
                exclude=exclude,
                by_alias=by_alias,
                skip_defaults=skip_defaults,
                custom_encoder=custom_encoder,
            )
            for v in obj  # type: ignore
        ]
    if isinstance(obj, dict):
        return {
            jsonable_encoder(
                k,
                include=include,
                exclude=exclude,
                by_alias=by_alias,
                skip_defaults=skip_defaults,
                custom_encoder=custom_encoder,
            ): jsonable_encoder(
                v,
                include=include,
                exclude=exclude,
                by_alias=by_alias,
                skip_defaults=skip_defaults,
                custom_encoder=custom_encoder,
            )
            for k, v in obj.items()  # type: ignore
        }
    if isinstance(obj, bytes):
        return base64.b64encode(obj).decode()
    if isinstance(obj, (set, frozenset)):
        return [
            jsonable_encoder(
                v,
                include=include,
                exclude=exclude,
                by_alias=by_alias,
                skip_defaults=skip_defaults,
                custom_encoder=custom_encoder,
            )
            for v in obj  # type: ignore
        ]
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, Enum):
        return obj.value
    if isinstance(obj, UUID):
        return str(obj)
    if isinstance(obj, type):
        return jsonable_encoder(
            obj.__name__,
            include=include,
            exclude=exclude,
            by_alias=by_alias,
            skip_defaults=skip_defaults,
            custom_encoder=custom_encoder,
        )

    return custom_encoder().default(obj)
