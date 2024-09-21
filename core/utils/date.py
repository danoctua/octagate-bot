from datetime import datetime, timedelta


def generate_expire_date(expire_in: int) -> datetime:
    return datetime.now() + timedelta(minutes=expire_in)
