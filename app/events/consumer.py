import json
import logging
from typing import Callable, Awaitable
from aiokafka import AIOKafkaConsumer

BOOTSTRAP_SERVERS = "localhost:19092"


class AlertConsumer:
    def __init__(
        self,
        topic: str,
        group_id: str = "triage-group",
        bootstrap_servers: str = BOOTSTRAP_SERVERS,
    ):
        self.topic = topic
        self.group_id = group_id
        self.bootstrap_servers = bootstrap_servers
        self.consumer = None
        self._running = False

    async def start(self):
        self.consumer = AIOKafkaConsumer(
            self.topic,
            bootstrap_servers=self.bootstrap_servers,
            group_id=self.group_id,
            auto_offset_reset="earliest",
            enable_auto_commit=False,
            value_deserializer=lambda x: json.loads(x.decode("utf-8")),
        )
        await self.consumer.start()
        self._running = True

    async def stop(self):
        self._running = False
        if self.consumer:
            await self.consumer.stop()

    async def consume(self, handler: Callable[[dict], Awaitable[None]]):
        if not self.consumer:
            raise RuntimeError("Consumer not started. Call start() first.")
        try:
            async for msg in self.consumer:
                if not self._running:
                    break
                logging.info(
                    f"[Consumer] Received alert payload from topic '{msg.topic}'"
                )
                await handler(msg.value)
                await self.consumer.commit()
        except Exception as e:
            logging.error(f"[Consumer Error] Failed to process message: {e}")
