from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, JSON, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class IncidentRecord(Base):
    __tablename__ = "incident_reports"

    id = Column(String, primary_key=True)
    service_name = Column(String, nullable=False)
    issue_description = Column(Text, nullable=False)
    summary = Column(Text, nullable=False)
    evidence = Column(JSON, nullable=False)
    root_cause = Column(Text, nullable=False)
    recommended_actions = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))