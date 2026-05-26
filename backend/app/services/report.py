import json
import os
from typing import Any

import httpx

from app.models.schemas import QualityFinding, RuleResult


def build_mitre_coverage(rule_results: list[RuleResult]) -> dict:
    tactics = {}
    for result in rule_results:
        item = tactics.setdefault(result.mitre_tactic, {"total": 0, "ready": 0, "partial": 0, "blocked": 0})
        item["total"] += 1
        if result.status == "실행 가능":
            item["ready"] += 1
        elif result.status == "부분 실행 가능":
            item["partial"] += 1
        else:
            item["blocked"] += 1
    for item in tactics.values():
        item["score"] = int(((item["ready"] + item["partial"] * 0.5) / max(item["total"], 1)) * 100)
    return tactics


def build_template_report(scores: dict[str, int], findings: list[QualityFinding], rule_results: list[RuleResult], coverage: dict) -> dict[str, str]:
    blocked = [r for r in rule_results if r.status != "실행 가능"]
    top_findings = ", ".join(f.message for f in findings[:3]) or "주요 결함 없음"
    weak_tactics = [name for name, item in coverage.items() if item["score"] < 70]
    return {
        "executive_summary": f"전체 로그 품질 점수는 {scores['log_quality']}점입니다. 주요 이슈는 {top_findings}입니다.",
        "technical_guide": f"우선 보완 대상은 누락 필드 정비, timestamp 표준화, 룰 요구 필드 매핑입니다. 실행 제한 룰은 {len(blocked)}개입니다.",
        "audit_summary": f"관측성 취약 영역은 {', '.join(weak_tactics) if weak_tactics else '없음'}입니다. 원문 로그 대신 진단 결과와 마스킹된 통계 기준으로 보고서를 생성했습니다.",
        "generator": "template"
    }


def build_report_payload(scores: dict[str, int], findings: list[QualityFinding], rule_results: list[RuleResult], coverage: dict) -> dict[str, Any]:
    return {
        "scores": scores,
        "findings": [finding.model_dump() for finding in findings[:10]],
        "rule_summary": {
            "total": len(rule_results),
            "ready": sum(1 for rule in rule_results if rule.status == "실행 가능"),
            "partial": sum(1 for rule in rule_results if rule.status == "부분 실행 가능"),
            "blocked": sum(1 for rule in rule_results if rule.status == "실행 불가")
        },
        "blocked_rules": [rule.model_dump() for rule in rule_results if rule.status != "실행 가능"][:10],
        "mitre_coverage": coverage
    }


def build_prompt(payload: dict[str, Any]) -> str:
    return (
        "너는 기업 보안관제/SOC 컨설팅 보고서를 작성하는 보안 분석가다. "
        "아래 JSON은 원문 로그가 아니라 마스킹된 진단 통계다. "
        "반드시 한국어로 답하고, JSON만 반환해라. "
        "반환 형식은 executive_summary, technical_guide, audit_summary 세 키만 사용한다. "
        "과장하지 말고 점수와 근거 중심으로 작성한다.\n\n"
        f"진단 데이터:\n{json.dumps(payload, ensure_ascii=False)}"
    )


async def call_ollama(prompt: str) -> dict[str, str]:
    base_url = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")
    model = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
    timeout = float(os.getenv("OLLAMA_TIMEOUT", "120"))
    body = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "format": "json",
        "options": {
            "temperature": 0.2,
            "num_ctx": 4096
        }
    }
    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.post(f"{base_url}/api/generate", json=body)
        response.raise_for_status()
        data = response.json()
        text = data.get("response", "{}")
        parsed = json.loads(text)
        return {
            "executive_summary": str(parsed.get("executive_summary", "")),
            "technical_guide": str(parsed.get("technical_guide", "")),
            "audit_summary": str(parsed.get("audit_summary", "")),
            "generator": f"ollama:{model}"
        }


async def build_report(scores: dict[str, int], findings: list[QualityFinding], rule_results: list[RuleResult], coverage: dict) -> dict[str, str]:
    fallback = build_template_report(scores, findings, rule_results, coverage)
    if os.getenv("OLLAMA_ENABLED", "true").lower() != "true":
        return fallback
    try:
        payload = build_report_payload(scores, findings, rule_results, coverage)
        return await call_ollama(build_prompt(payload))
    except Exception as exc:
        fallback["generator"] = f"template:fallback:{exc.__class__.__name__}"
        return fallback
