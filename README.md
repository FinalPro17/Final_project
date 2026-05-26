# LogSight AI MVP Ollama Edition

보안 로그 품질 진단 및 관측성 사각지대 탐지 플랫폼 MVP입니다.

## 실행

```bash
docker compose up --build
```

첫 실행 후 별도 터미널에서 모델을 내려받습니다.

```bash
docker exec -it logsight-ollama ollama pull llama3.1:8b
```

모델 다운로드 후 다시 분석을 실행하면 Ollama 기반 리포트가 생성됩니다.

- Frontend: http://localhost:5173
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Ollama: http://localhost:11434

## Ollama 설정

`docker-compose.yml`에서 모델을 바꿀 수 있습니다.

```yaml
OLLAMA_MODEL=llama3.1:8b
```

PC 사양이 낮으면 아래처럼 작은 모델로 바꾸고 pull 명령도 같은 모델명으로 실행합니다.

```yaml
OLLAMA_MODEL=phi3:mini
```

```bash
docker exec -it logsight-ollama ollama pull phi3:mini
```

## 구현 범위

- CSV, JSON, JSONL 로그 업로드
- 공통 필드 정규화
- 로그 타입 자동 분류
- 필드 누락, timestamp 오류, 중복, 수집 공백 탐지
- 룰 요구 필드 기반 실행 가능성 판정
- MITRE 전술별 관측성 점수 계산
- Ollama 기반 관리자용, 기술팀용, 감사용 리포트 생성
- Ollama 장애 시 템플릿 리포트로 자동 대체
- Docker Compose 배포

## 샘플

`samples/logs/web_access.csv`와 `samples/rules/default_rules.yaml`을 업로드하여 동작을 확인할 수 있습니다.

## 구조

```text
backend/app/api/routes.py
backend/app/services/parser.py
backend/app/services/normalizer.py
backend/app/services/quality.py
backend/app/services/rules.py
backend/app/services/report.py
frontend/src/main.jsx
```

## 리포트 생성 방식

분석 엔진은 원문 로그를 LLM에 보내지 않습니다. 점수, 품질 이슈, 룰 실행 가능성, MITRE 커버리지 같은 요약 통계만 Ollama 프롬프트에 전달합니다.

`backend/app/services/report.py`에서 `call_ollama()`가 `/api/generate`를 호출하고, 응답 JSON을 `executive_summary`, `technical_guide`, `audit_summary`로 반환합니다.
