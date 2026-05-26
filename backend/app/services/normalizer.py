import pandas as pd

FIELD_ALIASES = {
    "timestamp": ["timestamp", "time", "event_time", "@timestamp", "date", "datetime"],
    "user": ["user", "username", "account", "src_user", "target_user"],
    "src_ip": ["src_ip", "source_ip", "client_ip", "ip", "remote_addr"],
    "dst_ip": ["dst_ip", "destination_ip", "server_ip"],
    "event_id": ["event_id", "eventid", "event_code", "signature_id"],
    "action": ["action", "event_action", "outcome", "status"],
    "process": ["process", "process_name", "image", "command_line"],
    "url": ["url", "uri", "path", "request"],
    "method": ["method", "http_method", "verb"],
}

LOG_TYPE_FIELDS = {
    "windows_auth": {"event_id", "user", "timestamp"},
    "linux_auth": {"user", "src_ip", "timestamp"},
    "web_access": {"src_ip", "url", "method", "timestamp"},
    "dns": {"src_ip", "query", "timestamp"},
    "generic": {"timestamp"},
}

def normalize(df: pd.DataFrame) -> pd.DataFrame:
    columns = {c.lower().strip(): c for c in df.columns}
    renamed = {}
    for canonical, aliases in FIELD_ALIASES.items():
        for alias in aliases:
            if alias in columns:
                renamed[columns[alias]] = canonical
                break
    return df.rename(columns=renamed)

def detect_log_type(df: pd.DataFrame) -> str:
    fields = set(df.columns)
    best = "generic"
    best_score = 0
    for log_type, required in LOG_TYPE_FIELDS.items():
        score = len(fields & required)
        if score > best_score:
            best = log_type
            best_score = score
    return best
