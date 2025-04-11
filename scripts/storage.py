import os
import json
import gzip
import boto3
from botocore.exceptions import ClientError
from typing import Union, BinaryIO, Optional
import logging

logger = logging.getLogger(__name__)


def get_s3_client():
    """Initialize and return an S3 client using environment variables for authentication."""
    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=os.environ.get('S3_ACCESS'),
            aws_secret_access_key=os.environ.get('S3_SECRET')
        )
        return s3_client
    except Exception as e:
        logger.error(f"Failed to initialize S3 client: {e}")
        raise


S3_CLIENT = get_s3_client()
S3_BUCKET = os.environ.get('S3_BUCKET')


def store_object(data: Union[str, bytes], object_name: str) -> bool:
    """
    Upload data directly to an S3 bucket.

    Args:
        data: The data to upload (string or bytes)
        object_name: S3 object name

    Returns:
        True if successful, False otherwise
    """
    try:
        # Convert string to bytes if needed
        if isinstance(data, str):
            data = data.encode('utf-8')

        S3_CLIENT.put_object(Body=data, Bucket=S3_BUCKET, Key=object_name)
        logger.info(f"Successfully uploaded data to {S3_BUCKET}/{object_name}")
        return True
    except ClientError as e:
        logger.error(f"Error uploading data to S3: {e}")
        return False


def store_dict(data: dict, object_name: str) -> bool:
    """
    Upload a dictionary as a JSON object to an S3 bucket.

    Args:
        data: The dictionary to upload
        object_name: S3 object name
    Returns:
        True if successful, False otherwise
    """
    try:
        json_data = json.dumps(data)
        compressed_data = gzip.compress(json_data.encode('utf-8'))
        return store_object(compressed_data, object_name)
    except Exception as e:
        logger.error(f"Error uploading dictionary to S3: {e}")
        return False


def read_object(object_name: str) -> Optional[bytes]:
    """
    Read data from an S3 object.

    Args:
        object_name: S3 object name

    Returns:
        Object data as bytes or None if failed
    """
    try:
        response = S3_CLIENT.get_object(Bucket=S3_BUCKET, Key=object_name)
        data = response['Body'].read()
        logger.info(f"Successfully read object {S3_BUCKET}/{object_name}")
        return data
    except ClientError as e:
        logger.error(f"Error reading object from S3: {e}")
        return None


def read_dict(object_name: str) -> Optional[dict]:
    """
    Read a JSON object from an S3 bucket and decompress it.

    Args:
        object_name: S3 object name

    Returns:
        Dictionary if successful, None otherwise
    """
    try:
        compressed_data = read_object(object_name)
        if compressed_data:
            json_data = gzip.decompress(compressed_data)
            return json.loads(json_data.decode('utf-8'))
        return None
    except Exception as e:
        logger.error(f"Error reading dictionary from S3: {e}")
        return None


def list_objects(prefix: str = '') -> list:
    """
    List objects in an S3 bucket with optional prefix.

    Args:
        prefix: Object key prefix

    Returns:
        List of object keys
    """
    try:
        response = S3_CLIENT.list_objects_v2(Bucket=S3_BUCKET, Prefix=prefix)

        if 'Contents' in response:
            return [obj['Key'] for obj in response['Contents']]
        return []
    except ClientError as e:
        logger.error(f"Error listing objects in S3: {e}")
        return []

def check_object_exists(object_name: str) -> bool:
    """
    Check if an object exists in an S3 bucket.

    Args:
        object_name: S3 object name

    Returns:
        True if object exists, False otherwise
    """
    try:
        S3_CLIENT.head_object(Bucket=S3_BUCKET, Key=object_name)
        return True
    except ClientError:
        return False

def delete_object(object_name: str) -> bool:
    """
    Delete an object from an S3 bucket.

    Args:
        object_name: S3 object name

    Returns:
        True if successful, False otherwise
    """
    try:
        S3_CLIENT.delete_object(Bucket=S3_BUCKET, Key=object_name)
        logger.info(f"Successfully deleted {S3_BUCKET}/{object_name}")
        return True
    except ClientError as e:
        logger.error(f"Error deleting object from S3: {e}")
        return False


if __name__ == "__main__":
    store_dict({"foo": "bar"}, "test/hello.txt")
    data = read_dict("test/hello.txt")
    if data:
        print(data)
