import uuid
from dependency_injector.wiring import Provide

from fridonai_core.plugins.utilities.adapter_base import BaseAdapter
from libs.utils.redis import Publisher, QueueGetter
from libs.utils.redis.schemas import ResponseMessage


class BlockchainRedisSendWaitAdapter(BaseAdapter):

    async def send(
        self,  
        topic: str,
        params: dict, 
        *args, 
        pub: Publisher = Provide["publisher"],
        queue_getter: QueueGetter = Provide["queue_getter"],
        **kwargs,
    ) -> dict | str:
        queue_name = str(uuid.uuid4())
        await pub.publish(
            topic,
            str(
                ResponseMessage.from_params(
                    params["chat_id"],
                    params["wallet_id"],
                    None,
                    params["tx"],
                    queue_name,
                    {}
                )
            )
        )
        response = await queue_getter.get(queue_name=queue_name)
        return response
