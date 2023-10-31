from typing import AsyncGenerator, cast

import openai

from ..schema.schema import *
from ..services import APIClient
from ..utils import handle
from .functions import *


class ChatCompletion(OpenAIResource):
    """OpenAI Chat Completion API."""

    model: ChatModel = Field(default="gpt-3.5-turbo-16k")

    @handle
    async def run(self, text: str, context: str):  # type: ignore
        request = ChatCompletionRequest(
            messages=[Message(content=text), Message(content=context, role="system")]
        )
        response = await openai.ChatCompletion.acreate(**request.dict())  # type: ignore
        return ChatCompletionResponse(**response)  # type: ignore

    async def stream(self, text: str, context: str) -> AsyncGenerator[str, None]:
        request = ChatCompletionRequest(
            messages=[Message(content=text), Message(content=context, role="system")],
            stream=True,
        )
        response = await openai.ChatCompletion.acreate(**request.dict())  # type: ignore
        async for message in response:  # type: ignore
            data = message.choices[0].delta.get("content", "")  # type: ignore
            yield data  # type: ignore
            


class Completion(OpenAIResource):
    """OpenAI Completion API."""

    model: CompletionModel = Field(default="gpt-3.5-turbo-instruct")

    @handle
    async def run(self, text: str):  # type: ignore
        request = CompletionRequest(prompt=text)
        response = await openai.Completion.acreate(**request.dict())  # type: ignore
        return CompletionResponse(**response)  # type: ignore

    async def stream(self, text: str) -> AsyncGenerator[str, None]:
        request = CompletionRequest(prompt=text, stream=True)
        response = await openai.Completion.acreate(**request.dict())  # type: ignore
        async for message in response:  # type: ignore
            data = message.choices[0].get("text", "")  # type: ignore
            yield data  # type: ignore


class Embeddings(OpenAIResource):
    """OpenAI Embeddings API."""

    model: EmbeddingModel = Field(default="text-embedding-ada-002")

    @handle
    async def run(self, texts: List[str]) -> List[Vector]:  # type: ignore
        response = await openai.Embedding.acreate(input=texts, model=self.model)  # type: ignore
        return [r.embedding for r in response.data]  # type: ignore


class Image(OpenAIResource):
    """OpenAI Image API."""

    model: ImageModel = Field(default="dall-e")
    size: Size = Field(default="1024x1024")
    format: ImageFormat = Field(default="url")

    @handle
    async def run(self, text: str, n: int = 1) -> List[str]:  # type: ignore
        response = await openai.Image.acreate(prompt=text, n=n, size=self.size, response_format=self.format)  # type: ignore
        return [r[self.format] for r in response.data]  # type: ignore


class Audio(OpenAIResource):
    """OpenAI Audio API."""

    model: AudioModel = Field(default="whisper-1")

    @handle
    async def run(self, content: bytes, audioformat: AudioFormat = "wav") -> str:  # type: ignore
        response = await openai.Audio.acreate(self.model, AudioRequest(file=content, format=audioformat)())  # type: ignore
        return response.get("text", "")  # type: ignore


class VectorClient(APIClient):
    """

    A client for the vector database.

    Args:

        api_key (str): The API key.

        api_endpoint (str): The API endpoint.

    """

    base_url: str = Field(
        default_factory=lambda: os.getenv("PINECONE_API_URL", "https://api.pinecone.io")
    )
    headers: Dict[str, str] = Field(
        default_factory=lambda: {
            "api-key": os.getenv("PINECONE_API_KEY"),
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
    )

    @property
    def embeddings(self) -> Embeddings:
        """

        Returns the embeddings.

        Returns:

            Embeddings: The embeddings.

        """
        return Embeddings()
    @handle
    async def upsert(self, embeddings: List[Embedding]) -> UpsertResponse:
        """

        Upserts a list of vector embeddings.

        Args:

            embeddings (List[Embedding]): The vector embeddings.

        Returns:

            UpsertResponse: The upsert response.

        """
        response = await self.post(
            "/vectors/upsert",
            data={
                "vectors": [
                    UpsertRequest(
                        values=embedding.values, metadata=embedding.metadata
                    ).dict()
                    for embedding in embeddings
                ]
            },
        )
        assert response is not None, "Response is None"
        return UpsertResponse(**response)
    @handle
    async def query(
        self, expr: Query, vector: Vector, topK: int, includeMetadata: bool = True
    ) -> QueryResponse:
        """

        Queries the vector database.

        Args:

            expr (Query): The query expression.

            vector (Vector): The vector to query.

            topK (int): The number of results to return.

            includeMetadata (bool, optional): Whether to include metadata in the response. Defaults to True.

        Returns:

            QueryResponse: The query response.

        """

        payload = QueryRequest(
            topK=topK,
            filter=expr,  # type: ignore
            vector=vector,
            includeMetadata=includeMetadata,
        ).dict()
        response = await self.post(
            "/query",
            data=payload,
        )
        assert response is not None, "Response is None"
        return QueryResponse(**response)
    @handle
    async def search(self, text: str, namespace: str, top_k: int = 5) -> List[str]:
        """Search for a text into a namespace

        Args:
            text (str): The text to search
            namespace (str): The namespace to search into
            top_k (int, optional): The number of results to return. Defaults to 5.

        Returns:
            List[str]: The list of results
        """
        response = await self.query(
            expr=(QueryBuilder("namespace") == namespace).query,
            vector=(await self.embeddings.run([text]))[0],
            topK=top_k,
            includeMetadata=True,
        )

        return [match.metadata["text"] for match in response.matches]  # type: ignore
    @handle
    async def run(
        self,
        text: str,
        namespace: str,
        vector: Vector,
        action: Literal["query", "upsert"],
    ):
        if action == "query":
            response = await self.query(
                expr=(QueryBuilder("namespace") == namespace).query,
                vector=vector,
                topK=5,
                includeMetadata=True,
            )
            return [match.metadata["text"] for match in response.matches]  # type: ignore
        elif action == "upsert":
            response = await self.upsert(
                [
                    Embedding(
                        values=vector, metadata={"text": text, "namespace": namespace}
                    )
                ]
            )
            return response.upsertedCount
