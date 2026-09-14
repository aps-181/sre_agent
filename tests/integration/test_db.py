import asyncio
import pytest
from sqlalchemy import delete
from app.db.session import AsyncSessionLocal
from app.models.incident import IncidentRecord
from app.schemas.investigation import InvestigationResult
from app.db.repositories.incident_repository import IncidentRepository

TEST_SERVICE = "payment-gateway"


@pytest.mark.asyncio
async def test_incident_persistence():
    # Pre-test cleanup: clear any existing records for this service
    async with AsyncSessionLocal() as session:
        await session.execute(
            delete(IncidentRecord).where(IncidentRecord.service_name == TEST_SERVICE)
        )
        await session.commit()

    mock_result = InvestigationResult(
        summary="Payment service failing due to connection pool limits.",
        evidence=["Log: Connection pool exhausted"],
        root_cause="High traffic spikes depleted available DB connections.",
        recommended_actions=["Increase max_connections"],
    )

    try:
        async with AsyncSessionLocal() as session:
            repo = IncidentRepository(session)
            record = await repo.create_incident_record(
                service_name=TEST_SERVICE,
                issue_description="Payment gateway throwing 500 errors",
                result=mock_result,
            )

            assert record is not None
            assert record.id is not None
            assert record.service_name == TEST_SERVICE
            print(f"Integration test passed! Stored record ID: {record.id}")

    finally:
        # Post-test teardown: remove test record to leave DB clean
        async with AsyncSessionLocal() as session:
            await session.execute(
                delete(IncidentRecord).where(
                    IncidentRecord.service_name == TEST_SERVICE
                )
            )
            await session.commit()


if __name__ == "__main__":
    asyncio.run(test_incident_persistence())
