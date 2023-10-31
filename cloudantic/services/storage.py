# Full Path: cloudantic/cloudantic/services/storage.py
from boto3 import client  # type: ignore
from pydantic import BaseModel, Field  # pylint: disable=no-name-in-module

from ..utils import async_io, handle


class StorageBucket(BaseModel):
    """
    A class representing a storage bucket.

    Attributes:
    -----------
    bucket : str
        The name of the bucket.
    """

    bucket: str = Field(..., description="The name of the bucket")

    @property
    def client(self):
        """
        Returns an S3 client object.

        Returns:
        --------
        boto3.client
            An S3 client object.
        """
        return client("s3", region_name="us-east-1")

    @handle
    @async_io
    def create_bucket(self):
        """
        Creates a new bucket.

        Returns:
        --------
        dict
            A dictionary containing information about the newly created bucket.
        """
        return self.client.create_bucket(Bucket=self.bucket)

    @handle
    @async_io
    def delete_bucket(self):
        """
        Deletes the bucket.

        Returns:
        --------
        dict
            Metadata about the operation.
        """
        return self.client.delete_bucket(Bucket=self.bucket)

    @handle
    @async_io
    def list_buckets(self):
        """
        Lists all buckets.

        Returns:
        --------
        list
            A list of dictionaries containing information about each bucket.
        """
        return self.client.list_buckets()["Buckets"]

    @handle
    @async_io
    def upload_file(self, key: str, body: bytes):
        """
        Uploads a file to the bucket.

        Parameters:
        -----------
        key : str
            The key under which to store the file.
        file : UploadFile
            The file to upload.

        Returns:
        --------
        str
            A URL that can be used to download the uploaded file.
        """
        self.client.put_object(Bucket=self.bucket, Key=key, Body=body)
        return self.client.generate_presigned_url(
            "get_object", Params={"Bucket": self.bucket, "Key": key}
        )
