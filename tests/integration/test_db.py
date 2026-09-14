import asyncio
from app.db.session import engine, init_db, AsyncSessionLocal
from app.models.incident import Base
from app.schemas.investigation import InvestigationResult
from app.repositories.incident_repository import IncidentRepository


async def test_incident_persistence():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await init_db()

    mock_result = InvestigationResult(
        summary="Payment service failing due to connection pool limits.",
        evidence=["Log: Connection pool exhausted"],
        root_cause="High traffic spikes depleted available DB connections.",
        recommended_actions=["Increase max_connections"],
    )

    async with AsyncSessionLocal() as session:
        repo = IncidentRepository(session)
        record = await repo.create_report(
            service_name="payment-gateway",
            issue_description="Payment gateway throwing 500 errors",
            result=mock_result,
        )

        assert record is not None
        assert record.id is not None
        print(f"Integration test passed! Stored record ID: {record.id}")


if __name__ == "__main__":
    asyncio.run(test_incident_persistence())
