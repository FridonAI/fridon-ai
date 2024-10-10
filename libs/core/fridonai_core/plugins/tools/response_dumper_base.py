import uuid
import json
from typing import Any, Literal
from pydantic import BaseModel

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ResponseDumperOutput(BaseModel):
    type: Literal["local", "s3"]
    extension: Literal["json", None] = None
    id: str
    name: str
    path: str | None = None


class ResponseDumper(BaseModel):
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
            type="local",
            extension="json",
            id=temp_file_id,
            name=name,
            path=f"tmp/{temp_file_id}.json",
        )
    

class S3ResponseDumperOutput(ResponseDumperOutput):
    url: str

class S3ResponseDumper(ResponseDumper):
    def __init__(self, bucket_name: str, **kwargs):
        from aiobotocore.session import get_session
        self.bucket_name = bucket_name
        self.session = get_session()
        self.kwargs = kwargs

    async def dump(self, data: str | Any, name: str, key: str = "tool_responses") -> S3ResponseDumperOutput:
        temp_file_id = str(uuid.uuid4())[:8]
        s3_key = f"{key}/{temp_file_id}.json"
        try:
            json_data = json.dumps(data, ensure_ascii=False, indent=2)
            presigned_url = await self._upload_to_s3_gen_presigned_url(s3_key, json_data)
        except Exception as e:
            logger.error(f"Error dumping data to S3: {e} unsupported data type: {type(data)}")
            raise e

        return S3ResponseDumperOutput(
            type="s3",
            extension="json",
            id=temp_file_id,
            path=s3_key,
            name=name,
            url=presigned_url,
        )
    
    async def _upload_to_s3_gen_presigned_url(self, s3_key: str, data: str, presigned_url_expiration: int = 3600):
        async with self.session.create_client('s3', **self.kwargs) as s3_client:
            try:
                await s3_client.put_object(Bucket=self.bucket_name, Key=s3_key, Body=data)
                logger.info(f"Data uploaded to S3: {s3_key}")
                presigned_url = await s3_client.generate_presigned_url(
                    'get_object',
                    Params={'Bucket': self.bucket_name, 'Key': s3_key},
                    ExpiresIn=presigned_url_expiration
                )
                logger.info(f"Presigned URL generated: {presigned_url}")
                return presigned_url
            except Exception as e:
                logger.error(f"Error uploading to S3 or generating presigned URL: {e}")
                raise e
            