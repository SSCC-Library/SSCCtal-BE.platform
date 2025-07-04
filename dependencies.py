from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import hashlib
from enum import Enum

def korea_time():
    return datetime.now(ZoneInfo("Asia/Seoul"))

def seven_days_later():
    return (korea_time() + timedelta(days=7)).date()

def hash_phone_number(phone: str) -> str:
    return hashlib.sha256(phone.encode()).hexdigest()

class DeletionStatusEnum(str, Enum):
    ACTIVE = "ACTIVE"      # 사용 가능
    DELETED = "DELETED"    # 논리적으로 삭제됨