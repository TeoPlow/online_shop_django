import json
import logging


log = logging.getLogger(__name__)


def parse(request):
    """
    Эта функция обрабатывает данные, которые криво приходят от фронтенда.

    Приходит в виде:
    {"{\"name\":\"test\",\"username\":\"user\",\"password\":\"pass\"}": ""}

    Возвращает нормальный словарь.
    """
    try:
        log.debug(f"Request data: {request.data}")
        raw = list(request.data.keys())[0]
        data = json.loads(raw)
        return data
    except Exception:
        log.debug("Failed to parse request data, maybe is normal...")
        return request.data
