import asyncio
import pytest
from app.events.producer import AlertProducer
from app.events.consumer import AlertConsumer


@pytest.mark.asyncio
async def test_redpanda_event_pipeline():
    topic = "sre.alerts.test"
    received_events = []

    async def mock_alert_handler(payload: dict):
        received_events.append(payload)

    producer = AlertProducer()
    consumer = AlertConsumer(topic=topic, group_id="test-triage-group")

    await producer.start()
    await consumer.start()

    sample_alert = {
        "service_name": "checkout-service",
        "issue_description": "Database connection timeout during peak traffic.",
    }

    try:
        await producer.send_alert(topic=topic, payload=sample_alert)

        # Pull single message with timeout
        msg = await asyncio.wait_for(consumer.consumer.getone(), timeout=5.0)
        await mock_alert_handler(msg.value)
        await consumer.consumer.commit()

        assert len(received_events) == 1
        assert received_events[0]["service_name"] == "checkout-service"
        print("\nRedpanda messaging integration test passed!")

    finally:
        await producer.stop()
        await consumer.stop()


if __name__ == "__main__":
    asyncio.run(test_redpanda_event_pipeline())
