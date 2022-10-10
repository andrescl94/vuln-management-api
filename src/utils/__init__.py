from datetime import datetime
import pytz


TZ = pytz.timezone("America/Bogota")


def get_from_timestamp(timestamp: float) -> str:
    return datetime.fromtimestamp(timestamp).astimezone(tz=TZ).replace(
        microsecond=0
    ).isoformat()


def get_now_as_iso() -> str:
    return datetime.now().astimezone(tz=TZ).replace(microsecond=0).isoformat()


def get_now_timestamp() -> float:
    return datetime.now().astimezone(tz=TZ).timestamp()
