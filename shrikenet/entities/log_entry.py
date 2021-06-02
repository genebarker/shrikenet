from dataclasses import dataclass
from datetime import datetime


@dataclass
class LogEntry:
    oid: int
    time: datetime
    app_user_oid: int
    tag: str
    text: str
    usecase_tag: str
    app_user_name: str = None
