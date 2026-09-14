from pydantic import BaseModel


class InvestigationResult(BaseModel):
    summary: str
    evidence: list[str]
    root_cause: str
    recommended_actions: list[str]
