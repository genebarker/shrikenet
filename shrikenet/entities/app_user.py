from dataclasses import dataclass
from datetime import datetime


@dataclass
class AppUser:
    username: str
    name: str
    password_hash: str
    oid: int = None
    needs_password_change: bool = False
    is_locked: bool = False
    is_dormant: bool = False
    ongoing_password_failure_count: int = 0
    last_password_failure_time: datetime = None
