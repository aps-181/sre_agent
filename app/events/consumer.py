import asyncio
import json
import logging
from typing import Callable, Awaitable
from aiokafka import AIOKafkaConsumer

BOOTSTRAP_SERVERS = "localhost:19092"
logger = logging.getLogger(__name__)


class AlertConsumer:
    def __init__(
        self,
        topic: str,
        group_id: str = "triage-group",
        bootstrap_servers: str = BOOTSTRAP_SERVERS,
        max_retries: int = 3,
        backoff_base: float = 1.0,
    ):
        self.topic = topic
        self.group_id = group_id
        self.bootstrap_servers = bootstrap_servers
        self.max_retries = max_retries
        self.backoff_base = backoff_base
        self.consumer: AIOKafkaConsumer | None = None
        self._running = False

    async def start(self) -> None:
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
        logger.info(
            f"[Consumer] Started for topic '{self.topic}' (group_id: {self.group_id})"
        )

    async def stop(self) -> None:
        self._running = False
        if self.consumer:
            await self.consumer.stop()
        logger.info("[Consumer] Stopped.")

    async def consume(self, handler: Callable[[dict], Awaitable[None]]) -> None:
        if not self.consumer:
            raise RuntimeError("Consumer not started. Call start() first.")

        async for msg in self.consumer:
            if not self._running:
                break

            processed_successfully = False
            for attempt in range(1, self.max_retries + 1):
                try:
                    await handler(msg.value)
                    processed_successfully = True
                    break
                except Exception as e:
                    logger.warning(
                        f"[Consumer Retry {attempt}/{self.max_retries}] "
                        f"Handler failed for offset {msg.offset}: {e}"
                    )
                    if attempt < self.max_retries:
                        await asyncio.sleep(self.backoff_base * (2 ** (attempt - 1)))

            if processed_successfully:
                await self.consumer.commit()
                logger.debug(f"[Consumer] Offset committed: {msg.offset}")
            else:
                logger.critical(
                    f"[Consumer Paused] Failed offset {msg.offset} after {self.max_retries} retries. "
                    "Halting consumer loop to preserve uncommitted offset state."
                )
                self._running = False
                break
