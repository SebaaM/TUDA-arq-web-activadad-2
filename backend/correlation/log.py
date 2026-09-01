import json
import logging
from datetime import datetime

from .context import get_trace_context

# Logger dedicado a la trazabilidad de la API. Sus eventos están pensados para
# reconstruir una interacción concreta sin depender de logs textuales libres.
logger = logging.getLogger("tuda.trace")

LEVELS = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL,
}


def log_event(event, *, result=None, level="info", **metadata):
    # La trazabilidad se asocia al contexto activo de la request actual, de modo
    # que todos los eventos de una misma interacción comparten el mismo ID.
    trace = get_trace_context()
    record = {
        "timestamp": datetime.now().astimezone().isoformat(timespec="seconds"),
        "level": level,
        "event": event,
        "correlation_id": trace.correlation_id if trace else None,
        "method": trace.method if trace else None,
        "path": trace.path if trace else None,
        "result": result,
    }
    record.update(metadata)
    logger.log(LEVELS.get(level, logging.INFO), json.dumps(record, ensure_ascii=False))
    return record