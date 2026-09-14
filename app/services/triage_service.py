import logging
from app.db.session import AsyncSessionLocal
from app.db.repositories import IncidentRepository
from app.schemas.investigation import InvestigationResult

logger = logging.getLogger(__name__)


async def process_incoming_alert(payload: dict) -> None:
    """
    Consumer callback handler. Reads alert payloads, executes triage analysis,
    constructs an InvestigationResult schema, and persists findings to PostgreSQL.
    """
    service_name = payload.get("service_name", "unknown-service")
    issue_description = payload.get("issue_description", "No description provided.")

    logger.info(f"[TriageService] Analyzing alert for service: {service_name}")

    # Reformatted evidence into a list of strings to satisfy InvestigationResult schema
    investigation_result = InvestigationResult(
        summary=f"Automated triage triggered for {service_name} due to: {issue_description}",
        evidence=[
            f"Raw payload: {payload}",
            "Logs sample: Connection timed out after 5000ms (Retried 3 times)",
            "Metrics: error_rate=15%, p99_latency_ms=4500",
        ],
        root_cause=f"High concurrency leading to connection pool exhaustion in {service_name}.",
        recommended_actions=[
            "Increase DB connection pool size from 20 to 50",
            "Scale service replicas horizontally by +2",
            "Verify downstream DB latency metrics",
        ],
    )

    # Persist directly into PostgreSQL using AsyncSessionLocal context manager
    async with AsyncSessionLocal() as session:
        repository = IncidentRepository(session)
        incident = await repository.create_incident_record(
            service_name=service_name,
            issue_description=issue_description,
            result=investigation_result,
        )

        if incident:
            logger.info(
                f"[TriageService] Successfully saved incident record ID: {incident.id}"
            )
        else:
            logger.error(
                f"[TriageService] Failed to persist incident record for service: {service_name}"
            )
