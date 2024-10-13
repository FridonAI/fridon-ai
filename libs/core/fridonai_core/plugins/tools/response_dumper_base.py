import uuid
import json
from typing import Any, Literal
from pydantic import BaseModel

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ResponseDumperOutput(BaseModel):
    type: str
    source: Literal["local", "s3"]
    extension: Literal["json", None] = None
    id: str
    name: str
    path: str | None = None


class ResponseDumper:
    async def dump(self, data: Any, name: str, key: str) -> ResponseDumperOutput: ...



class LocalResponseDumperOutput(ResponseDumperOutput):
    pass


class LocalResponseDumper(ResponseDumper):
    async def dump(self, data: str | Any, name: str, key: str = "tmp") -> LocalResponseDumperOutput:
        temp_file_id = str(uuid.uuid4())[:8]
        try:
            with open(f"{key}/{temp_file_id}.json", 'w') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Error dumping data to local file: {e} unsupported data type: {type(data)}")
            raise e

        return ResponseDumperOutput(
            type=name,
            source="local",
            extension="json",
            id=temp_file_id,
            name=name,
            path=f"tmp/{name}-{temp_file_id}.json",
        )
    

class S3ResponseDumperOutput(ResponseDumperOutput):
    url: str

class S3ResponseDumper(ResponseDumper):
    def __init__(self, bucket_name: str = 'data.fridon.ai', **kwargs):
        from aiobotocore.session import get_session
        self.bucket_name = bucket_name
        self.session = get_session()
        self.kwargs = kwargs

    async def dump(self, data: str | Any, name: str, key: str = "tool_responses") -> S3ResponseDumperOutput:
        temp_file_id = str(uuid.uuid4())[:8]
        s3_key = f"{key}/{name}/{temp_file_id}.json"
        try:
            json_data = json.dumps(data, ensure_ascii=False, indent=2)
            await self._upload_to_s3(s3_key, json_data)
        except Exception as e:
            logger.error(f"Error dumping data to S3: {e} unsupported data type: {type(data)}")
            raise e

        return S3ResponseDumperOutput(
            type=name,
            source="s3",
            extension="json",
            id=temp_file_id,
            path=s3_key,
            name=name,
            url=f"https://data.fridon.ai/{s3_key}",
        )
    async def _upload_to_s3(self, s3_key: str, data: str):
        async with self.session.create_client('s3', **self.kwargs) as s3_client:
            try:
                await s3_client.put_object(
                    Bucket=self.bucket_name,
                    Key=s3_key,
                    Body=data,
                    ContentType='application/json'
                )
                logger.info(f"Data uploaded to S3: {s3_key}")
                return True
            except Exception as e:
                logger.error(f"Error uploading to S3 or generating presigned URL: {e}")
                raise e
            