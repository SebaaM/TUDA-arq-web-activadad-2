from contextvars import ContextVar


# El contexto de trazado se guarda por hilo/flujo de ejecución para que cada
# parte de la request pueda acceder al mismo correlation_id sin pasar el valor
# manualmente por todas las llamadas.
class TraceContext:
    __slots__ = ("correlation_id", "method", "path")

    def __init__(self, correlation_id: str, method: str, path: str):
        self.correlation_id = correlation_id
        self.method = method
        self.path = path


_current = ContextVar("tuda_trace_context", default=None)


def set_trace_context(trace: TraceContext):
    # El token devuelto permite restaurar el contexto anterior al finalizar la
    # ejecución de una request, evitando contaminación entre peticiones.
    return _current.set(trace)


def reset_trace_context(token) -> None:
    _current.reset(token)


def get_trace_context() -> TraceContext:
    # Se usa desde el logger para enriquecer cada evento con la misma trazabilidad
    # de la interacción actual.
    return _current.get()