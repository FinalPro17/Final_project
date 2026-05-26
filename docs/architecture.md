# Architecture

LogSight AI MVP는 Input, Normalization, Quality Engine, Coverage Engine, Report, Dashboard 계층으로 구성한다.

## Backend

FastAPI가 파일 업로드와 분석 API를 제공한다. 분석 결과는 현재 응답 기반으로 반환하며, 상용 단계에서는 PostgreSQL 저장과 작업 큐를 붙인다.

## Frontend

React/Vite 기반 단일 화면 대시보드다. 점수 카드, 품질 진단 결과, 룰 실행 가능성, 개선 리포트를 표시한다.

## Extension

Splunk, Elastic, Wazuh, Syslog API 연동은 커넥터 계층으로 분리하여 확장한다.
