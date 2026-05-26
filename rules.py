from pydantic import BaseModel
from typing import Any

class Rule(BaseModel):
    id: str
    title: str
    mitre_tactic: str
    required_fields: list[str]
    log_type: str | None = None

class RuleResult(BaseModel):
    id: str
    title: str
    status: str
    missing_fields: list[str]
    mitre_tactic: str

class QualityFinding(BaseModel):
    type: str
    severity: str
    message: str
    count: int = 0

class AnalysisResult(BaseModel):
    filename: str
    detected_log_type: str
    total_events: int
    fields: list[str]
    scores: dict[str, int]
    findings: list[QualityFinding]
    rule_results: list[RuleResult]
    mitre_coverage: dict[str, Any]
    report: dict[str, str]
