import yaml
from pathlib import Path
from app.models.schemas import Rule, RuleResult

DEFAULT_RULES = [
    Rule(id="WIN-001", title="Windows 로그인 실패 탐지", mitre_tactic="Credential Access", required_fields=["timestamp", "event_id", "user"], log_type="windows_auth"),
    Rule(id="LIN-001", title="Linux SSH 로그인 실패 탐지", mitre_tactic="Credential Access", required_fields=["timestamp", "user", "src_ip"], log_type="linux_auth"),
    Rule(id="WEB-001", title="웹 경로 스캐닝 탐지", mitre_tactic="Discovery", required_fields=["timestamp", "src_ip", "url", "method"], log_type="web_access"),
    Rule(id="PROC-001", title="의심 프로세스 실행 탐지", mitre_tactic="Execution", required_fields=["timestamp", "process", "user"], log_type=None),
    Rule(id="NET-001", title="외부 반출 의심 통신 탐지", mitre_tactic="Exfiltration", required_fields=["timestamp", "src_ip", "dst_ip"], log_type=None),
]

def load_rules(rule_text: str | None) -> list[Rule]:
    if not rule_text:
        return DEFAULT_RULES
    data = yaml.safe_load(rule_text)
    if isinstance(data, dict) and "rules" in data:
        data = data["rules"]
    return [Rule(**item) for item in data]

def evaluate_rules(fields: list[str], rules: list[Rule]) -> list[RuleResult]:
    field_set = set(fields)
    results = []
    for rule in rules:
        missing = [field for field in rule.required_fields if field not in field_set]
        if not missing:
            status = "실행 가능"
        elif len(missing) < len(rule.required_fields):
            status = "부분 실행 가능"
        else:
            status = "실행 불가"
        results.append(RuleResult(id=rule.id, title=rule.title, status=status, missing_fields=missing, mitre_tactic=rule.mitre_tactic))
    return results
