from __future__ import annotations

import os
from tempfile import NamedTemporaryFile
from typing import (Any, Dict, List, Literal, Set, Type, TypeAlias, TypeVar,
                    Union)
from uuid import uuid4

from pydantic import (BaseModel, Field,  # pylint: disable=no-name-in-module
                      root_validator)

from .typedef import *

# pylint: disable=no-name-in-module




Value: TypeAlias = Union[int, float, str, bool, List[str]]
QueryJoin: TypeAlias = Literal["$and", "$or"]
QueryWhere: TypeAlias = Literal[
    "$eq", "$ne", "$gt", "$gte", "$lt", "$lte", "$in", "$nin"
]
QueryKey: TypeAlias = Union[str, QueryWhere, QueryJoin]
QueryValue: TypeAlias = Union[Value, List[Value], "Query", List["Query"]]
Query: TypeAlias = Dict[QueryKey, QueryValue]
# Please write Sphinx documentation for this m

T = TypeVar("T")


class QueryBuilder(object):
    def __init__(self, field: str = None, query: Query = None):  # type: ignore
        """
        Initializes a new QueryBuilder instance.

        Args:
            field (str, optional): The field to query. Defaults to None.
            query (Query, optional): The query dictionary. Defaults to an empty dictionary.
        """
        self.field = field
        self.query = query if query else {}

    def __repr__(self) -> str:
        """Returns the string representation of the query."""
        return f"{self.query}"

    def __call__(self, field_name: str) -> QueryBuilder:
        """
        Creates a new QueryBuilder instance with a given field name.

        Args:
            field_name (str): The field name to query.

        Returns:
            QueryBuilder: A new QueryBuilder instance.
        """
        return QueryBuilder(field_name)

    def __and__(self, other: QueryBuilder) -> QueryBuilder:
        """
        Combines two queries using the $and operator.

        Args:
            other (QueryBuilder): Another QueryBuilder instance.

        Returns:
            QueryBuilder: A new QueryBuilder instance with the combined query.
        """
        return QueryBuilder(query={"$and": [self.query, other.query]})

    def __or__(self, other: QueryBuilder) -> QueryBuilder:
        """
        Combines two queries using the $or operator.

        Args:
            other (QueryBuilder): Another QueryBuilder instance.

        Returns:
            QueryBuilder: A new QueryBuilder instance with the combined query.
        """
        return QueryBuilder(query={"$or": [self.query, other.query]})

    def __eq__(self, value: Value) -> QueryBuilder:  # type: ignore
        """
        Creates a new QueryBuilder instance with the $eq operator.

        Args:
            value (Value): The value to query.

        Returns:
            QueryBuilder: A new QueryBuilder instance with the combined query.

        """
        return QueryBuilder(query={self.field: {"$eq": value}})

    def __ne__(self, value: Value) -> QueryBuilder:  # type: ignore
        """
        Creates a new QueryBuilder instance with the $ne operator.

        Args:
            value (Value): The value to query.

        Returns:
            QueryBuilder: A new QueryBuilder instance with the combined query.

        """
        return QueryBuilder(query={self.field: {"$ne": value}})

    def __lt__(self, value: Value) -> QueryBuilder:
        """
        Creates a new QueryBuilder instance with the $lt operator.

        Args:

            value (Value): The value to query.

        Returns:

            QueryBuilder: A new QueryBuilder instance with the combined query.


        """

        return QueryBuilder(query={self.field: {"$lt": value}})

    def __le__(self, value: Value) -> QueryBuilder:
        """
        Creates a new QueryBuilder instance with the $lte operator.

        Args:

            value (Value): The value to query.

        Returns:

            QueryBuilder: A new QueryBuilder instance with the combined query.

        """

        return QueryBuilder(query={self.field: {"$lte": value}})

    def __gt__(self, value: Value) -> QueryBuilder:
        """

        Creates a new QueryBuilder instance with the $gt operator.

        Args:

            value (Value): The value to query.

        Returns:

            QueryBuilder: A new QueryBuilder instance with the combined query.

        """

        return QueryBuilder(query={self.field: {"$gt": value}})

    def __ge__(self, value: Value) -> QueryBuilder:
        """

        Creates a new QueryBuilder instance with the $gte operator.

        Args:

            value (Value): The value to query.

        Returns:

            QueryBuilder: A new QueryBuilder instance with the combined query.

        """

        return QueryBuilder(query={self.field: {"$gte": value}})

    def in_(self, values: List[Value]) -> QueryBuilder:
        """

        Creates a new QueryBuilder instance with the $in operator.

        Args:

            values (List[Value]): The values to query.

        Returns:

            QueryBuilder: A new QueryBuilder instance with the combined query.

        """

        return QueryBuilder(query={self.field: {"$in": values}})

    def nin_(self, values: List[Value]) -> QueryBuilder:
        """

        Creates a new QueryBuilder instance with the $nin operator.

        Args:

            values (List[Value]): The values to query.

        Returns:

            QueryBuilder: A new QueryBuilder instance with the combined query.

        """

        return QueryBuilder(query={self.field: {"$nin": values}})


class UpsertRequest(BaseModel):
    """
    A request to upsert a vector.

    Args:
        id (str, optional): The ID of the vector. Defaults to a random UUID.
        values (Vector): The vector values.
        metadata (MetaData): The vector metadata.
    """

    id: str = Field(default_factory=lambda: str(uuid4()))
    values: Vector = Field(...)
    metadata: MetaData = Field(...)


class Embedding(BaseModel):
    """

    A vector embedding.

    Args:

        values (Vector): The vector values.

        metadata (MetaData): The vector metadata.

    """

    values: Vector = Field(...)
    metadata: MetaData = Field(...)


class QueryRequest(BaseModel):
    """
    A request to query vectors.

    Args:

        topK (int, optional): The number of results to return. Defaults to 10.

        filter (Query): The query filter.

        includeMetadata (bool, optional): Whether to include metadata in the response. Defaults to True.

        vector (Vector): The vector to query.

    """

    topK: int = Field(default=10)
    filter: Dict[str, Any] = Field(...)
    includeMetadata: bool = Field(default=True)
    vector: Vector = Field(...)


class QueryMatch(BaseModel):
    """

    A query match.

    Args:

        id (str): The ID of the vector.

        score (float): The match score.

        metadata (MetaData): The vector metadata.

    """

    id: str = Field(...)
    score: float = Field(...)
    metadata: MetaData = Field(...)


class QueryResponse(BaseModel):
    """

    A response to a query request.

    Args:

        matches (List[QueryMatch]): The query matches.

    """

    matches: List[QueryMatch] = Field(...)


class UpsertResponse(BaseModel):
    """

    A response to an upsert request.

    Args:

        upsertedCount (int): The number of vectors upserted.

    """

    upsertedCount: int = Field(...)


class CompletionRequest(BaseModel):
    model: CompletionModel = Field(default="gpt-3.5-turbo-instruct")
    prompt: str = Field(...)
    temperature: float = Field(default=0.2)
    max_tokens: int = Field(default=1024)
    stream: bool = Field(default=False)


class CompletionChoice(BaseModel):
    index: int = Field(...)
    finish_reason: str = Field(...)
    text: str = Field(...)


class CompletionUsage(BaseModel):
    prompt_tokens: int = Field(...)
    completion_tokens: int = Field(...)
    total_tokens: int = Field(...)


class CompletionResponse(BaseModel):
    id: str = Field(...)
    object: str = Field(...)
    created: int = Field(...)
    model: CompletionModel = Field(...)
    choices: List[CompletionChoice] = Field(...)
    usage: CompletionUsage = Field(...)


class Message(BaseModel):
    """
    Represents a message within the chatcompletion API pipeline.
    """

    role: Role = Field(default="user")
    content: str = Field(...)


class ChatCompletionRequest(BaseModel):
    model: ChatModel = Field(default="gpt-3.5-turbo-16k")
    messages: List[Message] = Field(...)
    temperature: float = Field(default=0.5)
    max_tokens: int = Field(default=512)
    stream: bool = Field(default=False)


class ChatCompletionUsage(BaseModel):
    """Token usage statistics for a chat completion API call."""

    prompt_tokens: int = Field(...)
    completion_tokens: int = Field(...)
    total_tokens: int = Field(...)


class ChatCompletionChoice(BaseModel):
    index: int = Field(...)
    message: Message = Field(...)
    finish_reason: str = Field(...)


class ChatCompletionResponse(BaseModel):
    id: str = Field(...)
    object: str = Field(...)
    created: int = Field(...)
    model: str = Field(...)
    choices: List[ChatCompletionChoice] = Field(...)
    usage: ChatCompletionUsage = Field(...)


class EmbeddingUssage(BaseModel):
    """Token usage statistics for an embedding API call."""

    prompt_tokens: int = Field(...)
    total_tokens: int = Field(...)


class CreateImageResponse(BaseModel):
    created: float = Field(...)
    data: List[Dict[ImageFormat, str]] = Field(...)


class CreateImageRequest(BaseModel):
    """Request to create an image from a prompt. Use default values for configuration unless specified."""

    prompt: str = Field(...)
    n: int = Field(default=1)
    size: Size = Field(default="1024x1024")
    response_format: ImageFormat = Field(default="url")


class FineTuneSample(BaseModel):
    messages: List[Message] = Field(..., max_items=3, min_items=2)

    @root_validator
    @classmethod
    def check_messages(cls: Type[BaseModel], values: Dict[str, Any]):
        roles: Set[Role] = set()
        for message in values["messages"]:
            roles.add(message.role)
        assert len(roles) == len(
            values["messages"]
        ), "All messages must be from different roles."
        return values


class FineTuneRequest(BaseModel):
    __root__: List[FineTuneSample] = Field(..., min_items=10, max_items=100000)

    def __call__(self):
        with NamedTemporaryFile("w", suffix=".json") as f:
            data = self.json()
            f.write(data)
            f.flush()
            return f


class AudioRequest(BaseModel):
    file: bytes = Field(...)
    format: AudioFormat = Field(default="mp3")

    def __call__(self):
        with NamedTemporaryFile("wb", suffix=f".{self.format}") as f:
            f.write(self.file)
            f.flush()
            assert len(f.read()) < 25 * 1024 * 1024, "File too large."
            return f
