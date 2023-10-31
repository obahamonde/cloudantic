"""
DynamoDB Object Document Mapper (ODM) for Python.
------------------------------------------------
This module provides a Pydantic model for DynamoDB.
"""
from __future__ import annotations

import json
from abc import ABC, abstractmethod
from datetime import datetime
from decimal import Decimal
from enum import Enum
from functools import cached_property
from typing import (Any, Dict, Generic, Iterable, List, Literal, Optional, Set,
                    Type, TypeVar, cast)
from uuid import UUID

from boto3 import Session
from boto3.dynamodb.types import TypeDeserializer, TypeSerializer
from dotenv import load_dotenv
from pydantic import (BaseConfig, BaseModel, Extra,  # pylint: disable=E0611
                      Field)
from typing_extensions import ParamSpec, override

from ..utils import async_io, handle
from .json import CloudEncoder, parse_json_hook

load_dotenv()


T = TypeVar("T")
D = TypeVar("D", bound="DynaModel")
P = ParamSpec("P")
Operator = Literal["=", ">", "<", ">=", "<=", "begins_with", "between", "contains"]


def emptystring() -> str:
    """
    Returns an empty string.

    :return: An empty string.
    :rtype: str
    """
    return ""


REGION = "us-east-1"
dynamodb = Session().client(service_name="dynamodb", region_name=REGION)  # type: ignore


class LazyProxy(Generic[T], ABC):
    """
    A generic abstract class for implementing lazy loading patterns.

    Attributes:
    -----------
    __proxied: T | None
        The proxied object, if it has been loaded.
    """

    def __init__(self) -> None:
        self.__proxied: T | None = None

    def __getattr__(self, attr: str) -> object:
        return getattr(self.__get_proxied__(), attr)

    def __repr__(self) -> str:
        return repr(self.__get_proxied__())

    def __dir__(self) -> Iterable[str]:
        return self.__get_proxied__().__dir__()

    def __get_proxied__(self) -> T:
        """
        Get the proxied object, loading it if necessary.

        Returns:
        --------
        T
            The proxied object.
        """
        proxied = self.__proxied
        if proxied is not None:
            return proxied

        self.__proxied = proxied = self.__load__()
        return proxied

    def __set_proxied__(self, value: T) -> None:
        self.__proxied = value

    def __as_proxied__(self) -> T:
        return cast(T, self)

    @abstractmethod
    def __load__(self) -> T:
        """
        Load the proxied object.

        Returns:
        --------
        T
            The proxied object.
        """


class DynamoDB(LazyProxy[Session], Generic[D]):
    """
    A class representing a DynamoDB Single Table Design pattern.

    Attributes:
        entities (Set[Type[D]]): A set of entity types.
        session (Session): A boto3 session object.
    """

    entities: Set[Type[D]] = set()
    session: Session

    def __init__(self, model: Type[D]) -> None:
        """
        Initializes a DynamoDB instance.

        Args:
            model (Type[D]): The entity type.
        """
        self.model = model
        self.session = self.__load__()
        super().__init__()

    def __load__(self) -> Session:
        """
        Loads a boto3 session.

        Returns:
            Session: A boto3 session object.
        """
        return Session()

    @classmethod
    def __class_getitem__(cls, item: Type[D]) -> Type[DynamoDB[D]]:
        """
        Adds an entity type to the entities set.

        Args:
            item (Type[D]): The entity type.

        Returns:
            Type[DynamoDB[D]]: The DynamoDB class.
        """
        cls.entities.add(item)
        return cls

    @property
    def __table_name__(self) -> str:
        """
        Returns the table name.

        Returns:
            str: The table name.
        """
        ents: List[str] = []
        for ent in self.entities:
            ents.append(ent.__name__)
            ents.sort()
        return "-".join(ents)

    @cached_property
    def serializer(self) -> TypeSerializer:
        """
        Returns a TypeSerializer instance.

        Returns:
            TypeSerializer: A TypeSerializer instance.
        """
        return TypeSerializer()

    @cached_property
    def deserializer(self) -> TypeDeserializer:
        """
        Returns a TypeDeserializer instance.

        Returns:
            TypeDeserializer: A TypeDeserializer instance.
        """
        return TypeDeserializer()

    @cached_property
    def client(self):
        """
        Returns a DynamoDB client.

        Returns:
            botocore.client.BaseClient: A DynamoDB client.
        """
        return self.session.client(service_name="dynamodb", region_name="us-east-1")  # type: ignore

    def serialize(self: DynamoDB[D], instance: D) -> Dict[str, Any]:
        """
        Serializes an instance into a DynamoDB item.

        Args:
            instance (D): The instance to serialize.

        Returns:
            Dict[str, Any]: The serialized instance.
        """
        return self.serializer.serialize(instance.to_dict())["M"]  # type: ignore

    def deserialize(self: DynamoDB[D], data: Dict[str, Any]) -> D:
        """
        Deserializes a DynamoDB item into a dictionary representation of an instance.

        Args:
            data (Dict[str, Any]): The data to deserialize.

        Returns:
            D: The deserialized data.
        """
        return self.deserializer.deserialize({"M": data})  # type: ignore

    @staticmethod
    def create_all(name: str) -> None:
        """
        Creates the table.

        Args:
            name (str): The table name.
        """
        tables = dynamodb.list_tables()["TableNames"]
        if name not in tables:
            dynamodb.create_table(
                TableName=name,
                AttributeDefinitions=[
                    {"AttributeName": "pk", "AttributeType": "S"},
                    {"AttributeName": "sk", "AttributeType": "S"},
                ],
                KeySchema=[
                    {"AttributeName": "pk", "KeyType": "HASH"},
                    {"AttributeName": "sk", "KeyType": "RANGE"},
                ],
                BillingMode="PAY_PER_REQUEST",
            )
            dynamodb.get_waiter("table_exists").wait(TableName=name)

    def get(self: DynamoDB[D], pk: str, sk: str) -> D:
        """
        Gets the dictionary representation of an instance.

        Args:
            pk (str): The partition key.
            sk (str): The sort key.

        Returns:
            D: The instance.
        """
        response = self.client.get_item(
            TableName=self.__table_name__,
            Key={
                "pk": self.serializer.serialize(pk),
                "sk": self.serializer.serialize(sk),
            },
        )
        return self.deserialize(response.get("Item", {}))

    def put(self: DynamoDB[D], instance: D) -> None:
        """
        Puts an instance.

        Args:
            instance (D): The instance to put.
        """
        self.client.put_item(
            TableName=self.__table_name__, Item=self.serialize(instance)
        )

    def delete(self: DynamoDB[D], pk: str, sk: str) -> None:
        """
        Deletes an instance.

        Args:
            pk (str): The partition key.
            sk (str): The sort key.
        """
        self.client.delete_item(
            TableName=self.__table_name__,
            Key={
                "pk": self.serializer.serialize(pk),
                "sk": self.serializer.serialize(sk),
            },
        )

    def query(
        self: DynamoDB[D],
        pk: str,
        sk: Optional[str] = None,
        operator: Optional[Operator] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> List[D]:
        """
        Queries the table.

        Args:
            pk (str): The partition key.
            sk (Optional[str]): The sort key.
            operator (Optional[Operator]): The DynamoDB query operator.
            limit (Optional[int]): The limit of items to return.
            offset (Optional[int]): The offset of the query.

        Returns:
            List[D]: The dictionary representation of the instances.
        """
        key_condition = "pk = :pk"
        expression_values = {":pk": {"S": pk}}

        if sk:
            if operator == "begins_with":
                key_condition += " AND begins_with ( sk, :sk )"
                expression_values[":sk"] = {"S": sk}
            elif operator == "between":
                key_condition += " AND sk BETWEEN :sk0 AND :sk1"
                from_, to_ = sk.split("-")
                expression_values[":sk0"] = {"S": from_}
                expression_values[":sk1"] = {"S": to_}
            elif operator in ["=", ">", "<", ">=", "<="]:
                key_condition += f" AND sk {operator} :sk"
                expression_values[":sk"] = {"S": sk}
            else:
                raise ValueError("Invalid sort key")
        if limit:
            key_condition += f" LIMIT {limit}"
        if offset:
            key_condition += f" OFFSET {offset}"
        response = self.client.query(
            TableName=self.__table_name__,
            KeyConditionExpression=key_condition,
            ExpressionAttributeValues=expression_values,
        )
        return [self.deserialize(item) for item in response.get("Items", [])]

    def scan(
        self: DynamoDB[D], limit: Optional[int] = None, offset: Optional[int] = None
    ) -> List[D]:
        """
        Scans the table.

        Args:
            limit (Optional[int]): The limit.
            offset (Optional[int]): The offset.

        Returns:
            List[D]: The dictionary representation of the instances.
        """
        scan_kwargs: Dict[str, Any] = {}
        if limit:
            scan_kwargs["Limit"] = limit
        if offset:
            scan_kwargs["Offset"] = offset
        response = self.client.scan(TableName=self.__table_name__, **scan_kwargs)
        return [self.deserialize(item) for item in response.get("Items", [])]


class DynaModel(BaseModel):
    """
    A Pydantic model for DynamoDB.

    Attributes:
    - pk (str): The partition key.
    - sk (str): The sort key.
    - db (DynamoDB): The DynamoDB instance.
    """

    pk: str = Field(default_factory=emptystring, alias="_pk")
    sk: str = Field(default_factory=emptystring, alias="_sk")

    def __init__(self, **kwargs: Any) -> None:
        """
        Initializes the model.

        Args:
        - **kwargs: The keyword arguments.
        """
        super().__init__(**kwargs)
        self.pk = self.pk_
        self.sk = self.sk_

    def to_dict(
        self,
        by_alias: bool = False,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        exclude_none: bool = True,
    ) -> Dict[str, Any]:
        """
        Converts the model to a dictionary.

        Args:
        - by_alias (bool): Whether to use the alias.
        - exclude_unset (bool): Whether to exclude unset values.
        - exclude_defaults (bool): Whether to exclude default values.
        - exclude_none (bool): Whether to exclude None values.

        Returns:
        - dict: The dictionary representation of the model.
        """
        return super().dict(
            by_alias=by_alias,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
        )

    @override
    def dict(self, **kwargs: Any):
        """
        Converts the model to a dictionary.

        Args:
        - **kwargs: The keyword arguments.

        Returns:
        - dict: The dictionary representation of the model.
        """
        exclude_set: set[Any] = kwargs.pop("exclude", set()) or set()
        exclude_set.update({"pk", "sk"})
        dct = super().dict(exclude=exclude_set, **kwargs)
        return json.loads(
            json.dumps(dct, cls=CloudEncoder), object_hook=parse_json_hook
        )

    @override
    def json(self, **kwargs: Any):
        """
        Converts the model to a JSON string.

        Args:
        - **kwargs: The keyword arguments.

        Returns:
        - str: The JSON string representation of the model.
        """
        exclude_set: set[Any] = kwargs.pop("exclude", set()) or set()
        exclude_set.update({"pk", "sk"})
        return super().json(
            exclude=exclude_set, encoder=CloudEncoder().default, **kwargs
        )

    class Config(BaseConfig):
        """
        The configuration class for the model.

        Attributes:
        - allow_population_by_field_name (bool): Whether to allow population by field name.
        - json_encoders (dict): The JSON encoders.
        - use_enum_values (bool): Whether to use enum values.
        - extra (str): The extra configuration.
        """

        allow_population_by_field_name = True
        json_encoders = {
            datetime: lambda dt: dt.astimezone().isoformat(),
            Decimal: float,
            UUID: str,
            Enum: lambda e: e.value,
        }
        use_enum_values = True
        extra = Extra.allow

        @staticmethod
        def schema_extra(schema: Dict[str, Any], _: Type[DynaModel]) -> None:  # type: ignore
            """
            Adds extra schema information.

            Args:
            - schema (dict): The schema.
            - model_class (Type[DynaModel]): The model class.
            """
            schema["properties"].pop("_pk")
            schema["properties"].pop("_sk")

    @classmethod
    def __init_subclass__(cls: Type[D], **kwargs: Any) -> None:
        """
        Initializes the subclass.

        Args:
        - **kwargs: The keyword arguments.
        """
        super().__init_subclass__(**kwargs)
        cls.db = DynamoDB[cls](cls)

    @property
    def pk_(self) -> str:
        """
        Gets the partition key.

        Returns:
        - str: The partition key.
        """
        for field in self.__fields__.values():
            if field.field_info.extra.get("pk"):
                key = getattr(self, field.name)
                if isinstance(key, Enum):
                    key = key.value
                return self.__class__.__name__ + "#" + str(key)
        raise ValueError("No partition key found")

    @property
    def sk_(self) -> str:
        """
        Gets the sort key.

        Returns:
        - str: The sort key.
        """
        keys: List[str] = []
        for field in self.__fields__.values():
            if field.field_info.extra.get("sk"):
                key = getattr(self, field.name)
                if isinstance(key, Enum):
                    key = key.value
                keys.append(str(key))
        if len(keys) == 0:
            raise ValueError("No sort key found")
        return "#".join(keys)

    @handle
    @async_io
    def put(self: D) -> D:
        """
        Puts the model in the database.

        Returns:
        - D: The model.
        """
        self.db.put(self)  # type: ignore / MyPy complains
        return self

    @classmethod
    @handle
    @async_io
    def delete(cls: Type[D], pk: str, sk: str) -> None:
        """
        Deletes the model from the database.

        Args:
        - pk (str): The partition key.
        - sk (str): The sort key.
        """
        prefix = cls.__name__ + "#"
        cls.db.delete(prefix + pk, sk)

    @classmethod
    @handle
    @async_io
    def get(cls: Type[D], pk: str, sk: str) -> D:
        """
        Gets the model from the database.

        Args:
        - pk (str): The partition key.
        - sk (str): The sort key.

        Returns:
        - D: The model.
        """
        prefix = cls.__name__ + "#"
        data = cls.db.get(prefix + pk, sk)
        return cls(**data)

    @classmethod
    @handle
    @async_io
    def query(
        cls: Type[D],
        pk: str,
        sk: Optional[str] = None,
        operator: Optional[Operator] = None,
    ) -> List[D]:
        """
        Queries the database.

        Args:
        - pk (str): The partition key.
        - sk (Optional[str]): The sort key.
        - operator (Operator): The operator.

        Returns:
        - List[D]: The list of models.
        """
        prefix = cls.__name__ + "#"
        data = cls.db.query(prefix + pk, sk, operator)
        return [cls(**item) for item in data]

    @classmethod
    @handle
    @async_io
    def scan(cls: Type[D], **kwargs: Any) -> List[D]:
        """
        Scans the database.

        Args:
        - **kwargs: The keyword arguments.

        Returns:
        - List[D]: The list of models.
        """
        data = cls.db.scan(**kwargs)
        return [cls(**item) for item in data]

    def __repr__(self) -> str:
        """
        Gets the string representation of the model.

        Returns:
        - str: The string representation of the model.
        """
        return self.json()

    def __str__(self) -> str:
        """
        Gets the string representation of the model.

        Returns:
        - str: The string representation of the model.
        """
        return self.json()

    @classmethod
    def __table_name__(cls) -> str:
        """
        Gets the table name.

        Returns:
        - str: The table name.
        """
        ents: List[str] = []
        for ent in cls.__subclasses__():
            ents.append(ent.__name__)
            ents.sort()
        return "-".join(ents)

    @classmethod
    @handle
    @async_io
    def create_table(cls) -> str:
        """
        Creates the table.

        Returns:
        - str: The result message.
        """
        try:
            table_name = cls.__table_name__()
            dynamodb.create_table(
                TableName=table_name,
                AttributeDefinitions=[
                    {"AttributeName": "pk", "AttributeType": "S"},
                    {"AttributeName": "sk", "AttributeType": "S"},
                ],
                KeySchema=[
                    {"AttributeName": "pk", "KeyType": "HASH"},
                    {"AttributeName": "sk", "KeyType": "RANGE"},
                ],
                BillingMode="PAY_PER_REQUEST",
                StreamSpecification={
                    "StreamEnabled": True,
                    "StreamViewType": "NEW_AND_OLD_IMAGES",
                },
            )
            dynamodb.update_time_to_live(
                TableName=table_name,
                TimeToLiveSpecification={
                    "Enabled": True,
                    "AttributeName": "ttl",
                },
            )
            dynamodb.get_waiter("table_exists").wait(TableName=table_name)
            return f"Table {cls.__table_name__()} created successfully"
        except Exception:  # pylint: disable=W0718
            return f"Table {cls.__table_name__()} already exists"

    @classmethod
    @handle
    @async_io
    def drop_table(cls) -> bool:
        """
        Drops the table.

        Returns:
        - bool: Whether the table was dropped successfully.
        """
        try:
            dynamodb.delete_table(TableName=cls.__table_name__())
            dynamodb.get_waiter("table_not_exists").wait(TableName=cls.__table_name__())
            return True
        except Exception:  # pylint: disable=W0718
            return False
