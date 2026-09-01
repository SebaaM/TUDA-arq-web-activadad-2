import uuid

from .context import TraceContext, reset_trace_context, set_trace_context
from .log import log_event

# Encabezado observable para clientes y soporte: permite correlacionar request,
# response y logs de la misma interacción sin cambiar los contratosREST actuales.
CORRELATION_ID_HEADER = "X-Correlation-ID"


class CorrelationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Si el cliente ya envía un ID, se conserva exactamente. En caso contrario,
        # la API genera uno nuevo para mantener trazabilidad completa.
        correlation_id = request.headers.get(CORRELATION_ID_HEADER)
        if not correlation_id:
            correlation_id = str(uuid.uuid4())

        # Se guarda en la request para que las vistas y servicios puedan
        # consultarlo en el mismo flujo de ejecución.
        request.correlation_id = correlation_id
        token = set_trace_context(
            TraceContext(
                correlation_id=correlation_id,
                method=request.method,
                path=request.path,
            )
        )

        # El evento inicial marca la llegada de la interacción y permite seguir la
        # secuencia desde la entrada hasta la salida.
        log_event("request_received")

        try:
            response = self.get_response(request)
        except Exception:
            # Si ocurre un error no controlado, la evidencia aún mantiene el mismo
            # correlation_id para diagnosticar la falla.
            log_event("request_completed", result="error")
            raise
        else:
            # Se devuelve el mismo valor al cliente para que la observación de la
            # respuesta pueda relacionarse directamente con el request y los logs.
            log_event("request_completed", result=str(response.status_code))
            response[CORRELATION_ID_HEADER] = correlation_id
            return response
        finally:
            # Se limpia el contexto para evitar que un ID de una request contamine
            # la siguiente, manteniendo la trazabilidad localizada por interacción.
            reset_trace_context(token)