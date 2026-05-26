import io
import json
import pandas as pd
from fastapi import UploadFile, HTTPException

MAX_FILE_SIZE = 10 * 1024 * 1024
ALLOWED_EXTENSIONS = {".csv", ".json", ".jsonl", ".log"}

async def read_upload(file: UploadFile) -> pd.DataFrame:
    name = file.filename or ""
    lower = name.lower()
    if not any(lower.endswith(ext) for ext in ALLOWED_EXTENSIONS):
        raise HTTPException(status_code=400, detail="지원하지 않는 파일 형식입니다.")
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="파일 크기는 10MB 이하만 지원합니다.")
    text = content.decode("utf-8", errors="replace")
    if lower.endswith(".csv"):
        return pd.read_csv(io.StringIO(text))
    if lower.endswith(".jsonl") or lower.endswith(".log"):
        rows = []
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                rows.append({"raw": line})
        return pd.DataFrame(rows)
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=400, detail="JSON 파싱 실패") from exc
    if isinstance(data, list):
        return pd.DataFrame(data)
    if isinstance(data, dict):
        return pd.DataFrame(data.get("events", [data]))
    raise HTTPException(status_code=400, detail="분석 가능한 JSON 구조가 아닙니다.")
