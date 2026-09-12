import uuid
import sys
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.incident import IncidentRecord
from app.schemas.investigation import InvestigationResult

class IncidentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_report(
        self, 
        service_name: str, 
        issue_description: str, 
        result: InvestigationResult
    ) -> IncidentRecord | None:
        try:
            record = IncidentRecord(
                id=str(uuid.uuid4()),
                service_name=service_name,
                issue_description=issue_description,
                summary=result.summary,
                evidence=result.evidence,
                root_cause=result.root_cause,
                recommended_actions=result.recommended_actions
            )
            self.db.add(record)
            await self.db.commit()
            await self.db.refresh(record)
            return record
        except Exception as e:
            await self.db.rollback()
            print(f"[DB Error] Failed to persist report: {e}", file=sys.stderr)
            return None