from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Generic, List, Literal, Optional, Type, TypeVar

from boto3 import client  # type: ignore
from boto3.dynamodb.types import TypeDeserializer
from pydantic import (BaseConfig, BaseModel, Extra,  # pylint: disable=E0611
                      Field)

from ..utils import async_io, handle
from .odm import DynaModel

# es

D = TypeVar("D", bound=DynaModel)

StreamStatus = Literal["ENABLED", "DISABLED", "ENABLING", "DISABLING"]
StreamViewType = Literal["NEW_IMAGE", "OLD_IMAGE", "NEW_AND_OLD_IMAGES", "KEYS_ONLY"]
KeySchemaKeyType = Literal["HASH", "RANGE"]
ShardIteratorType = Literal[
    "TRIM_HORIZON", "LATEST", "AT_SEQUENCE_NUMBER", "AFTER_SEQUENCE_NUMBER"
]

EventName = Literal["INSERT", "MODIFY", "REMOVE"]

# TypeDefs


class TypeDef(BaseModel):
    """
    A class representing a type definition.

    Attributes:
                    Config (BaseConfig): A configuration class for the TypeDef.
    """

    ResponseMetadata: Any = Field(default=None)

    class Config(BaseConfig):
        """
        A configuration class for the TypeDef.
        - extra: Allow extra fields.
        - json_encoders: A dictionary of custom JSON encoders.
        """

        extra = Extra.allow
        json_encoders = {
            datetime: lambda v: v.astimezone().isoformat(),
        }


class SequenceNumberRangeTypeDef(TypeDef):
    """
    Defines a sequence number range for a DynamoDB data stream.
    """

    StartingSequenceNumber: Optional[str]
    EndingSequenceNumber: Optional[str]


class ShardTypeDef(TypeDef):
    """
    Defines the structure of a shard in an DynamoDB data stream.

    Attributes:
    - ShardId (str): The unique identifier of the shard.
    - SequenceNumberRange (SequenceNumberRangeTypeDef): The range of sequence numbers for the shard.
    - ParentShardId (Optional[str]): The unique identifier of the shard's parent shard, if any.
    """

    ShardId: str
    SequenceNumberRange: SequenceNumberRangeTypeDef
    ParentShardId: Optional[str]


class KeySchemaTypeDef(TypeDef):
    """
    Defines the schema for a key in a DynamoDB table.

    Attributes:
    - AttributeName (str): The name of the attribute.
    - KeyType (KeySchemaKeyType): The type of key (HASH or RANGE).
    """

    AttributeName: str
    KeyType: KeySchemaKeyType


class DynamoValueTypeDef(TypeDef):
    """
    A class representing the type definition of a DynamoDB value.

    Attributes:
                    S (Optional[str]): A string value.
                    N (Optional[str]): A number value.
                    B (Optional[bytes]): A binary value.
                    SS (Optional[List[str]]): A set of string values.
                    NS (Optional[List[str]]): A set of number values.
                    BS (Optional[List[bytes]]): A set of binary values.
                    M (Optional[Dict[str, DynamoValueTypeDef]]): A map of attribute values.
                    L (Optional[List[DynamoValueTypeDef]]): A list of attribute values.
                    NULL (Optional[bool]): A null value.
                    BOOL (Optional[bool]): A boolean value.
    """

    S: Optional[str]
    N: Optional[str]
    B: Optional[bytes]
    SS: Optional[List[str]]
    NS: Optional[List[str]]
    BS: Optional[List[bytes]]
    M: Optional[Dict[str, DynamoValueTypeDef]]
    L: Optional[List[DynamoValueTypeDef]]
    NULL: Optional[bool]
    BOOL: Optional[bool]

    def keys(self):
        """
        Returns the keys of the fields in the stream.
        Intended for backwards compatibility with the `TypedDict` class implemented by `boto3`.
        """
        return self.__fields__.keys()

    def values(self):
        """
        Returns a list of the values of the fields in the stream.
        Intended for backwards compatibility with the `TypedDict` class implemented by `boto3`.
        """
        return self.__fields__.values()

    def items(self):
        """
        Returns a list of the items of the fields in the stream.
        Intended for backwards compatibility with the `TypedDict` class implemented by `boto3`.
        """
        return self.__fields__.items()

    def __getitem__(self, key: str):
        """
        Returns the value of the field with the given key.
        Intended for backwards compatibility with the `TypedDict` class implemented by `boto3`.
        """
        return self.dict()[key]


DynamoValueTypeDef.update_forward_refs()


class DynamoDBTypeDef(TypeDef):
    """
    A class representing the type definition of a DynamoDB event.

    Attributes:
    - ApproximateCreationDateTime (datetime): The approximate date and time when the event was created.
    - Keys (Dict[str, DynamoValueTypeDef]): The primary key attributes for the item that was modified.
    - NewImage (Dict[str, DynamoValueTypeDef]): The item in the DynamoDB table as it appeared after it was modified.
    - OldImage (Optional[Dict[str, DynamoValueTypeDef]]): The item in the DynamoDB table as it appeared before it was modified.
    - SequenceNumber (str): The sequence number of the stream record.
    - SizeBytes (int): The size of the stream record, in bytes.
    - StreamViewType (StreamViewType): The type of data from the modified DynamoDB item that was captured in this stream record.
    """

    ApproximateCreationDateTime: datetime
    Keys: Dict[str, DynamoValueTypeDef]
    NewImage: Dict[str, DynamoValueTypeDef]
    OldImage: Optional[Dict[str, DynamoValueTypeDef]]
    SequenceNumber: str
    SizeBytes: int
    StreamViewType: StreamViewType


class UserIdentityTypeDef(TypeDef):
    """
    A class representing the type definition of a user identity.

    Attributes:
    - PrincipalId (str): A unique identifier for the entity that made the call.
    - Type (str): The type of the identity.
    """

    PrincipalId: str
    Type: str


class StreamDescriptionTypeDef(TypeDef):
    """
    A class representing the type definition of a DynamoDB stream description.

    Attributes:
    - StreamArn (str): The Amazon Resource Name (ARN) for the stream.
    - StreamLabel (str): A timestamp, in ISO 8601 format, for this stream.
    - StreamStatus (StreamStatus): Indicates the current status of the stream, one of ENABLED, DISABLED, ENABLING, or DISABLING.
    - StreamViewType (StreamViewType): Indicates the format of the records within this stream, one of NEW_IMAGE, OLD_IMAGE, NEW_AND_OLD_IMAGES, or KEYS_ONLY.
    - CreationRequestDateTime (datetime): The date and time when the request to create this stream was issued.
    - TableName (str): The DynamoDB table with which the stream is associated.
    - KeySchema (List[KeySchemaTypeDef]): The key schema for the DynamoDB table with which the stream is associated.
    - Shards (List[ShardTypeDef]): The shards that comprise the stream.
    - LastEvaluatedShardId (Optional[str]): The shard ID of the item where the operation stopped, inclusive of the previous result set. Use this value to start a new operation, excluding this value in the new request.
    - StreamDescription (Optional[str]): The stream description.
    """

    StreamArn: str
    StreamLabel: str
    StreamStatus: StreamStatus
    StreamViewType: StreamViewType
    CreationRequestDateTime: datetime
    TableName: str
    KeySchema: List[KeySchemaTypeDef] = Field(
        default=[
            {"AttributeName": "pk", "KeyType": "HASH"},
            {"AttributeName": "sk", "KeyType": "RANGE"},
        ]
    )
    Shards: List[ShardTypeDef] = Field(default=[])
    LastEvaluatedShardId: Optional[str]
    StreamDescription: Optional[str]


class ListStreamReturnTypeDef(TypeDef):
    """
    A class representing the type definition of a DynamoDB stream.

    Attributes:
    - StreamArn (str): The Amazon Resource Name (ARN) for the stream.
    - StreamLabel (str): A timestamp, in ISO 8601 format, for this stream.
    - TableName (str): The DynamoDB table with which the stream is associated.
    """

    StreamArn: str
    StreamLabel: str
    TableName: str


# Request/Response


class DescribeStreamsRequest(TypeDef):
    """
    A class representing the type definition of a request to describe a DynamoDB stream.

    Attributes:
    - StreamArn (str): The Amazon Resource Name (ARN) for the stream.
    - Limit (Optional[int]): The maximum number of shard objects to return.
    - ExclusiveStartShardId (Optional[str]): The shard ID of the first item that this operation will evaluate. Use the value that was returned for LastEvaluatedShardId in the previous operation.
    """

    StreamArn: str
    Limit: Optional[int] = Field(default=None)
    ExclusiveStartShardId: Optional[str] = Field(default=None)


class RecordTypeDef(TypeDef):
    """
    A class representing the type definition of a DynamoDB stream record.

    Attributes:
    - eventID (str): A globally unique identifier for the event that was recorded in this stream record.
    - eventName (EventName): The type of data modification that was performed on the DynamoDB table:
                    - INSERT - a new item was added to the table.
                    - MODIFY - one or more of an existing item's attributes were modified.
                    - REMOVE - the item was deleted from the table
    - eventVersion (str): The version number of the stream record format. This number is updated whenever the structure of Record is modified.
    - eventSource (str): The AWS service from which the stream record originated. For DynamoDB Streams, this is aws:dynamodb.
    - awsRegion (str): The region in which the GetRecords request was received.
    - dynamodb (DynamoDBTypeDef): The main body of the stream record, containing all of the DynamoDB-specific fields.
    - userIdentity (Optional[UserIdentityTypeDef]): Items that are deleted by the Time to Live process after expiration have the following fields:
                    - Records[].userIdentity.type "Service"
                    - Records[].userIdentity.principalId "dynamodb.amazonaws.com"
    """

    eventID: str
    eventName: EventName
    eventVersion: str
    eventSource: str
    awsRegion: str
    dynamodb: DynamoDBTypeDef
    userIdentity: Optional[UserIdentityTypeDef]


class DescribeStreamsResponse(TypeDef):
    """
    A class representing the type definition of a response to a request to describe a DynamoDB stream.

    Attributes:
    - StreamDescription (StreamDescriptionTypeDef): A complete description of the stream.
    """

    StreamDescription: StreamDescriptionTypeDef


class GetShardIteratorRequest(TypeDef):
    """
    A class representing the type definition of a request to get a shard iterator for a DynamoDB stream.

    Attributes:
    - StreamArn (str): The Amazon Resource Name (ARN) for the stream.
    - ShardId (str): The identifier of the shard.
    - ShardIteratorType (ShardIteratorType): Determines how the shard iterator is used to start reading stream records from the shard:
                    - TRIM_HORIZON - Start reading at the last (untrimmed) stream record, which is the oldest record in the shard. In DynamoDB Streams, there is a 24 hour limit on data retention. Stream records whose age exceeds this limit are subject to removal (trimming) from the stream.
                    - LATEST - Start reading just after the most recent stream record in the shard, so that you always read the most recent data in the shard.
                    - AT_SEQUENCE_NUMBER - Start reading at the position denoted by a specific sequence number, provided in the value StartingSequenceNumber.
                    - AFTER_SEQUENCE_NUMBER - Start reading right after the position denoted by a specific sequence number, provided in the value StartingSequenceNumber.
    - StartingSequenceNumber (Optional[str]): The sequence number of a stream record in the shard from which to start reading.
    """

    StreamArn: str
    ShardId: str
    ShardIteratorType: ShardIteratorType
    SequenceNumber: Optional[str] = Field(default=None)


class GetShardIteratorResponse(TypeDef):
    """
    A class representing the type definition of a response to a request to get a shard iterator for a DynamoDB stream.

    Attributes:
    - ShardIterator (str): The position in the shard from which to start reading stream records sequentially. A shard iterator specifies this position using the sequence number of a stream record in a shard.
    """

    ShardIterator: str


class GetRecordsRequest(TypeDef):
    """
    A class representing the type definition of a request to get records from a DynamoDB stream.

    Attributes:
    - ShardIterator (str): A shard iterator that was retrieved from a previous GetShardIterator operation. This iterator can be used to access the stream records in this shard.
    - Limit (Optional[int]): The maximum number of records to return from the shard. The upper limit is 1000.
    """

    ShardIterator: str
    Limit: Optional[int] = Field(default=None)


class GetRecordsResponse(TypeDef):
    """
    A class representing the type definition of a response to a request to get records from a DynamoDB stream.

    Attributes:
    - Records (List[RecordTypeDef]): The stream records from the shard, which were retrieved using the shard iterator.
    - NextShardIterator (str): The next position in the shard from which to start sequentially reading stream records. If set to null, the shard has been closed and the requested iterator will not return any more data.
    """

    Records: List[RecordTypeDef] = Field(default=[])
    NextShardIterator: str


class ListStreamsRequest(TypeDef):
    """
    A class representing the type definition of a request to list DynamoDB streams.

    Attributes:
    - TableName (str): The name of the table whose streams are to be listed.
    - Limit (Optional[int]): The maximum number of streams to return. The upper limit is 100.
    - ExclusiveStartStreamArn (Optional[str]): The ARN (Amazon Resource Name) of the first item that this operation will evaluate. Use the value that was returned for LastEvaluatedStreamArn in the previous operation.
    """

    TableName: str
    Limit: Optional[int] = Field(default=None)
    ExclusiveStartStreamArn: Optional[str] = Field(default=None)


class ListStreamResponse(TypeDef):
    """
    A class representing the type definition of a response to a request to list DynamoDB streams.

    Attributes:
    - Streams (List[ListStreamReturnTypeDef]): A list of stream descriptors associated with the current account and endpoint.
    - LastEvaluatedStreamArn (Optional[str]): The stream ARN of the item where the operation stopped, inclusive of the previous result set. Use this value to start a new operation, excluding this value in the new request.
    """

    Streams: List[ListStreamReturnTypeDef] = Field(default=[])
    LastEvaluatedStreamArn: Optional[str] = Field(default=None)


class DynamoDBStreams(Generic[D]):
    """
    The Generic DynamoDBStreams Client class responsible for handling all the operations related to dealing with streams.

    Attributes:
    - __table_name__ (str): The name of the table associated with the stream.
    - model (Type[D]): The model associated with the stream.

    Methods:
    - list_streams: Returns a list of streams.
    - describe_stream: Returns information about a stream, including the current status of the stream, its Amazon Resource Name (ARN), the composition of its shards, and its corresponding DynamoDB table.
    - get_shard_iterator: Returns a shard iterator.
    - get_records: Returns the stream records from a given shard iterator.
    - generator: A generator that yields the records from a given table on 'DynaModel' format.

    Primarily this class is intended to be used together with 'Server-Sent Events' to stream data from a given table through a FastAPI endpoint.
    [NOTE]: This streaming mechanism is weakly consistent, meaning that it may miss some records, to make it robust enough for a production environment, you should implement another service on top of it such as 'Kinesis Data Firehose' or 'Kinesis Data Streams'.
    """

    def __init__(self, model: Type[D]):
        self.__table_name__ = model.__table_name__()
        self.model = model

    @property
    def client(self):
        """
        'client' property that returns a DynamoDBStreams client.
        """
        return client("dynamodbstreams")

    @handle
    @async_io
    def list_streams(self, request: ListStreamsRequest) -> ListStreamResponse:
        all_streams = []
        last_evaluated_stream_arn = None
        
        def fetch_streams(request: ListStreamsRequest) -> Dict[str, Any]:
            return self.client.list_streams(**request.dict(exclude_none=True))
        
        while True:
            response = fetch_streams(request)
            all_streams.extend(response.get("Streams", []))
            last_evaluated_stream_arn = response.get("LastEvaluatedStreamArn", None)
            
            if last_evaluated_stream_arn is None:
                break
                
        return ListStreamResponse(
            Streams=all_streams, LastEvaluatedStreamArn=last_evaluated_stream_arn
        )


    @async_io
    def describe_stream(self, request: DescribeStreamsRequest):
        """
        'describe_stream' method that returns information about a stream, including the current status of the stream, its Amazon Resource Name (ARN), the composition of its shards, and its corresponding DynamoDB table. 'request' is a 'DescribeStreamsRequest' object. 'response' is a 'DescribeStreamsResponse' object.
        [NOTE]: We aren't using the 'async_io' decorator here since it will block the event loop on a single threaded development environment.
        """
        response = self.client.describe_stream(**request.dict(exclude_none=True))
        return DescribeStreamsResponse(**response)  # type: ignore

    @handle
    @async_io
    def get_shard_iterator(self, request: GetShardIteratorRequest):
        """
        'get_shard_iterator' method that returns a shard iterator. 'request' is a 'GetShardIteratorRequest' object. 'response' is a 'GetShardIteratorResponse' object.
        [NOTE]: We aren't using the 'async_io' decorator here since it will block the event loop on a single threaded development environment.
        """
        response = self.client.get_shard_iterator(**request.dict(exclude_none=True))
        return GetShardIteratorResponse(**response)

    @handle
    @async_io
    def get_records(self, request: GetRecordsRequest):
        """
        'get_records' method that returns the stream records from a given shard iterator. 'request' is a 'GetRecordsRequest' object. 'response' is a 'GetRecordsResponse' object.
        [NOTE]: We aren't using the 'async_io' decorator here since it will block the event loop on a single threaded development environment.
        """
        response = self.client.get_records(**request.dict(exclude_none=True))
        return GetRecordsResponse(**response)  # type: ignore / MyPy complains

    async def generator(self, table_name: str):
        """
        Main method that will be exposed through the FastAPI endpoint. It returns a generator that yields the records from a given table on 'DynaModel' format.
        [NOTE]: Intended to be used together with 'Server-Sent Events' to stream data from a given table through a FastAPI endpoint over a multi-threaded ASGI server, it's constrained due to it's lack of robustness, to make it robust enough for a production environment, you should implement another service on top of it such as 'Kinesis Data Firehose' or 'Kinesis Data Streams'.
        [TODO]: Implement a hook to enable the user to implement a custom service on top of it.
        [TODO]: Constraint it to handle a single StreamArn.
        """
        streams = (
            await self.list_streams(ListStreamsRequest(TableName=table_name))
        ).Streams
        for stream in streams:
            stream_arn = stream.StreamArn
            shards = (
                await self.describe_stream(DescribeStreamsRequest(StreamArn=stream_arn))
            ).StreamDescription.Shards
            for shard in shards:
                shard_id = shard.ShardId
                shard_iterator = (
                    await self.get_shard_iterator(
                        GetShardIteratorRequest(
                            StreamArn=stream_arn,
                            ShardId=shard_id,
                            ShardIteratorType="TRIM_HORIZON",
                        )
                    )
                ).ShardIterator
                while True:
                    records = (
                        await self.get_records(
                            GetRecordsRequest(ShardIterator=shard_iterator)
                        )
                    ).Records
                    for record in records:
                        data = record.dynamodb.NewImage
                        data_ = TypeDeserializer().deserialize({"M": data})
                        yield self.model(**data_)
                    shard_iterator = (
                        await self.get_records(
                            GetRecordsRequest(ShardIterator=shard_iterator)
                        )
                    ).NextShardIterator
