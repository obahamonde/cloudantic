from abc import ABC, abstractmethod
from typing import Any, Dict, List, Literal, TypeAlias, TypeVar, Union

from pydantic import BaseModel  # pylint: disable=no-name-in-module
from typing_extensions import ParamSpec

ImageModel: TypeAlias = Literal["dall-e"]
CompletionModel: TypeAlias = Literal["gpt-3.5-turbo-instruct", "davinci-002"]
ChatModel: TypeAlias = Literal["gpt-4", "gpt-3.5-turbo", "gpt-3.5-turbo-16k"]
EmbeddingModel: TypeAlias = Literal["text-embedding-ada-002"]
AudioModel: TypeAlias = Literal["whisper-1"]
Model: TypeAlias = Union[
    ChatModel, EmbeddingModel, AudioModel, CompletionModel, ImageModel
]
Role: TypeAlias = Literal["user", "system", "assistant", "function"]
Size: TypeAlias = Literal["256x256", "512x512", "1024x1024"]
ImageFormat: TypeAlias = Literal["url", "base64"]
AudioFormat: TypeAlias = Literal["mp3", "mp4", "mpeg", "mpga", "m4a", "wav", "webm"]
Vector: TypeAlias = List[float]
MetaDataValue: TypeAlias = Union[str, int, float, bool, List[str]]
MetaData: TypeAlias = Dict[str, MetaDataValue]

M = TypeVar("M", bound=Model)
P = ParamSpec("P")


class OpenAIResource(ABC, BaseModel):
    model: M  # type: ignore

    @abstractmethod
    async def run(self, *args: Any, **kwargs: Any) -> Any:
        ...
