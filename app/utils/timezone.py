from datetime import datetime
import pytz

IST = pytz.timezone('Asia/Kolkata')


def get_ist_now() -> datetime:
    return datetime.now(IST)


def convert_to_ist(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        # If naive, assume UTC
        dt = pytz.utc.localize(dt)
    return dt.astimezone(IST)


def parse_datetime_to_ist(dt_input) -> datetime:
    from datetime import datetime as dt_cls
    try:
        if isinstance(dt_input, dt_cls):
            dt = dt_input
        else:
            dt = dt_cls.fromisoformat(dt_input.replace('Z', '+00:00'))
        return convert_to_ist(dt)
    except Exception as e:
        raise ValueError(f"Invalid datetime format: {dt_input}. Use ISO format (e.g., 2025-06-15T10:00:00Z)")
