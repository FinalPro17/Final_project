import pandas as pd
from app.models.schemas import QualityFinding

REQUIRED_BASE_FIELDS = ["timestamp"]

def quality_analysis(df: pd.DataFrame) -> tuple[list[QualityFinding], dict[str, int]]:
    findings: list[QualityFinding] = []
    total = max(len(df), 1)
    missing_required = [field for field in REQUIRED_BASE_FIELDS if field not in df.columns]
    for field in missing_required:
        findings.append(QualityFinding(type="missing_field", severity="critical", message=f"필수 필드 누락: {field}", count=total))
    null_count = int(df.isna().sum().sum())
    if null_count:
        findings.append(QualityFinding(type="null_value", severity="major", message="빈 값이 포함되어 있습니다.", count=null_count))
    duplicate_count = int(df.duplicated().sum())
    if duplicate_count:
        findings.append(QualityFinding(type="duplicate", severity="minor", message="중복 이벤트가 존재합니다.", count=duplicate_count))
    timestamp_errors = 0
    gap_count = 0
    if "timestamp" in df.columns:
        ts = pd.to_datetime(df["timestamp"], errors="coerce", utc=True)
        timestamp_errors = int(ts.isna().sum())
        if timestamp_errors:
            findings.append(QualityFinding(type="timestamp_error", severity="major", message="파싱 불가능한 timestamp가 존재합니다.", count=timestamp_errors))
        ordered = ts.dropna().sort_values()
        if len(ordered) >= 2:
            gaps = ordered.diff().dt.total_seconds().fillna(0)
            gap_count = int((gaps > 3600).sum())
            if gap_count:
                findings.append(QualityFinding(type="collection_gap", severity="major", message="1시간 이상 수집 공백이 감지되었습니다.", count=gap_count))
    quality_score = 100
    quality_score -= min(40, len(missing_required) * 25)
    quality_score -= min(20, int(null_count / total * 10))
    quality_score -= min(20, int(timestamp_errors / total * 100))
    quality_score -= min(10, duplicate_count)
    quality_score -= min(10, gap_count * 3)
    quality_score = max(0, quality_score)
    scores = {
        "log_quality": quality_score,
        "investigation_readiness": max(0, min(100, int((len(df.columns) / 8) * 100)))
    }
    return findings, scores
