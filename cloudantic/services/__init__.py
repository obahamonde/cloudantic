from ..schema.schema import *
from .apiclient import APIClient
from .functions import *
from .kinesis import KinesisStream
from .openai import *
from .storage import StorageBucket


class Agent(BaseModel):
    namespace: str = Field(...)
    chat_completion: ChatCompletion = Field(default_factory=ChatCompletion)
    completion: Completion = Field(default_factory=Completion)
    embeddings: Embeddings = Field(default_factory=Embeddings)
    audio: Audio = Field(default_factory=Audio)
    image: Image = Field(default_factory=Image)
    vector: VectorClient = Field(default_factory=VectorClient)

    async def run(self, text: str) -> AsyncGenerator[str, None]:
        try:
            async for message in self.chat_completion.stream(text, context="You are a helpful assistant"):
                yield message
            #response_vector = (await self.embeddings.run([string]))[0]
            #await self.vector.run(
            #    text=string,
            #    namespace=self.namespace,
            #    vector=response_vector,
            #    action="upsert",
            #)
        except Exception as e:
            yield e.__class__.__name__ + ": " + str(e)


__all__ = [
    "Agent",
	"APIClient",
	"Audio",
	"ChatCompletion",
	"Completion",
	"Embeddings",
	"Image",
	"KinesisStream",
	"StorageBucket",
	"VectorClient",
]
