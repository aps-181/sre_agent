import asyncio
import pytest
from sqlalchemy import select, delete
from app.events.producer import AlertProducer
from app.events.consumer import AlertConsumer
from app.services.triage_service import process_incoming_alert
from app.db.session import AsyncSessionLocal
from app.models.incident import IncidentRecord


@pytest.mark.asyncio
async def test_redpanda_event_pipeline():
    topic = "sre.alerts.test"
    target_service = "payment-gateway-service"

    # Pre-test cleanup to remove stale state from previous runs
    async with AsyncSessionLocal() as session:
        await session.execute(
            delete(IncidentRecord).where(IncidentRecord.service_name == target_service)
        )
        await session.commit()

    producer = AlertProducer()
    consumer = AlertConsumer(topic=topic, group_id="test-event-consumption-group")

    await producer.start()
    await consumer.start()

    # Pass actual production triage service handler directly into background consumer loop
    consumer_task = asyncio.create_task(
        consumer.consume(handler=process_incoming_alert)
    )

    sample_alert = {
        "service_name": target_service,
        "issue_description": "High latency on payment processing endpoint.",
    }

    try:
        # 1. Publish real payload through producer
        await producer.send_alert(topic=topic, payload=sample_alert)

        # 2. Poll PostgreSQL until production handler writes the record
        record = None
        for _ in range(10):
            await asyncio.sleep(0.5)
            async with AsyncSessionLocal() as session:
                stmt = select(IncidentRecord).where(
                    IncidentRecord.service_name == target_service
                )
                result = await session.execute(stmt)
                record = result.scalars().first()
                if record:
                    break

        # 3. Assert real side-effects in PostgreSQL
        assert record is not None
        assert record.service_name == target_service
        assert (
            record.issue_description == "High latency on payment processing endpoint."
        )
        assert record.root_cause is not None

    finally:
        # Teardown background tasks & client connections
        consumer_task.cancel()
        await consumer.stop()
        await producer.stop()

        # Post-test database cleanup to leave DB state clean
        async with AsyncSessionLocal() as session:
            await session.execute(
                delete(IncidentRecord).where(
                    IncidentRecord.service_name == target_service
                )
            )
            await session.commit()


if __name__ == "__main__":
    asyncio.run(test_redpanda_event_pipeline())
