from fastapi import APIRouter, UploadFile, File
from app.models.schemas import AnalysisResult
from app.services.parser import read_upload
from app.services.normalizer import normalize, detect_log_type
from app.services.quality import quality_analysis
from app.services.rules import load_rules, evaluate_rules
from app.services.report import build_mitre_coverage, build_report

router = APIRouter()

@router.post("/analyze", response_model=AnalysisResult)
async def analyze(log_file: UploadFile = File(...), rule_file: UploadFile | None = File(default=None)):
    df = await read_upload(log_file)
    df = normalize(df)
    log_type = detect_log_type(df)
    findings, scores = quality_analysis(df)
    rule_text = None
    if rule_file:
        rule_text = (await rule_file.read()).decode("utf-8", errors="replace")
    rules = load_rules(rule_text)
    rule_results = evaluate_rules(list(df.columns), rules)
    ready = sum(1 for r in rule_results if r.status == "실행 가능")
    partial = sum(1 for r in rule_results if r.status == "부분 실행 가능")
    scores["detection_readiness"] = int(((ready + partial * 0.5) / max(len(rule_results), 1)) * 100)
    coverage = build_mitre_coverage(rule_results)
    scores["mitre_observability"] = int(sum(item["score"] for item in coverage.values()) / max(len(coverage), 1))
    scores["remediation_priority"] = 100 - min(scores["log_quality"], scores["detection_readiness"], scores["mitre_observability"])
    report = await build_report(scores, findings, rule_results, coverage)
    return AnalysisResult(filename=log_file.filename or "upload", detected_log_type=log_type, total_events=len(df), fields=list(df.columns), scores=scores, findings=findings, rule_results=rule_results, mitre_coverage=coverage, report=report)
