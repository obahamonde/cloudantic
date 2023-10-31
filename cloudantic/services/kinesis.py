import time
from typing import Generator, Literal
from uuid import uuid4

from boto3 import client  # type: ignore
from pydantic import BaseModel, Field  # pylint: disable=no-name-in-module

from ..utils import async_io, handle  # type: ignore

kinesis = client("kinesis", region_name="us-east-1")
N = 1


class KinesisStream(BaseModel):
    """
    First class Interface for Working with Kinesis Streams.
    """

    stream_name: str = Field(
        default_factory=lambda: str(uuid4()), description="The name of the stream"
    )
    shard_count: int = Field(
        default=N, description="The number of shards in the stream"
    )
    shard_iterator_type: Literal["TRIM_HORIZON", "LATEST"] = Field(
        default="TRIM_HORIZON", description="The shard iterator type"
    )

    @handle
    @async_io
    def create_stream(self):
        """
        `create_stream`
        ---------------
        Creates a stream with the given name.
        """
        return kinesis.create_stream(
            StreamName=str(self.stream_name), ShardCount=int(self.shard_count)
        )

    @handle
    @async_io
    def wait_for_stream(self: "KinesisStream") -> None:
        """
        `wait_for_stream`
        -----------------
        Waits for the stream to become active.
        """
        while True:
            response = kinesis.describe_stream(StreamName=self.stream_name)
            if response["StreamDescription"]["StreamStatus"] == "ACTIVE":
                break
            time.sleep(1)

    @handle
    @async_io
    def put_records(self, data: bytes):
        """
        `put_records`
        -------------
        Puts records into the stream. Can be anything from video, audio, text, or images. The protocol to consume it must be implemented by the server client.
        """
        kinesis.put_record(StreamName=self.stream_name, Data=data, PartitionKey=str(N))

    @handle
    @async_io
    def get_shard_id(self):
        """
        `get_shard_id`
        --------------
        Gets the shard id for the given stream name.
        A needed step on the subscription pipeline.
        """
        return kinesis.describe_stream(StreamName=self.stream_name)[
            "StreamDescription"
        ]["Shards"][0]["ShardId"]

    @handle
    @async_io
    def get_shard_iterator(self, shard_id: str):
        """
        `get_shard_iterator`
        --------------------
        Gets the shard iterator for the given shard id.
        A needed step on the subscription pipeline.
        """
        return kinesis.get_shard_iterator(
            StreamName=self.stream_name,
            ShardId=shard_id,
            ShardIteratorType=self.shard_iterator_type,
        )["ShardIterator"]

    @handle
    @async_io
    def list_streams(self):
        """
        `list_streams`
        --------------
        Lists all the streams in the account, meant for debugging purposes, don't expose this to the public.
        """
        return kinesis.list_streams()["StreamNames"]

    def get_records(self, shard_iterator: str) -> Generator[bytes, None, None]:
        """
        `get_records`
        -------------
        Generator that yields records from the stream.
        """
        while True:
            response = kinesis.get_records(ShardIterator=shard_iterator, Limit=2)

            for record in response["Records"]:
                yield record["Data"]

            shard_iterator = response["NextShardIterator"]
            time.sleep(1)

    @handle
    @async_io
    def delete_stream(self):
        """
        `delete_stream`
        ---------------
        Deletes an stream when it is no longer needed. For example, when all subscribers have disconnected.
        """
        kinesis.delete_stream(StreamName=self.stream_name)

    @handle
    async def open(self):
        """
        `open`
        ------
        Creates a stream with the given name and waits for it to become active.
        """
        await self.create_stream()
        await self.wait_for_stream()

    @handle
    async def pub(self, data: bytes):
        """
        `pub`
        -----
        Publishes data to the stream. Can be anything from video, audio, text, or images. The protocol to consume it must be implemented by the server client.
        """
        await self.put_records(data)

    async def sub(self):
        """
        `sub`
        -----
        Subscribes to the stream and yields the records as they come in.
        Meant to be a long lived connection to a destination client such as Server Sent Events or WebSockets. Must be explicitly closed.
        """
        shard_id = await self.get_shard_id()
        shard_iterator = await self.get_shard_iterator(shard_id)
        for record in self.get_records(shard_iterator):
            yield record

    @handle
    async def close(self):
        """
        `close`
        --------
        Deletes the stream. Streams are meant to be ephemeral yet long-lived connections to a destination client such a browser.
        [TODO]: Implement `Digital Asset Management` to store the data in a more permanent way.
        """
        await self.delete_stream()
