import type {
	Activity,
	ApiError,
	ApiErrorCode,
	ApiResult,
	Enrollment,
} from "../types/activity";

/**
 * Cliente de la API TUDA.
 *
 * - En el servidor (durante el build) se usa `API_BUILD_URL`, una URL
 *   absoluta: Node no sufre restricciones CORS.
 * - En el navegador la isla usa `PUBLIC_API_URL` (ruta relativa servida a
 *   través del proxy de Vite configurado en astro.config.mjs), porque la API
 *   no envía cabeceras CORS y el backend no puede modificarse.
 *
 * No se agregan endpoints nuevos: sólo los documentados en API.md.
 */

const BUILD_BASE: string =
	import.meta.env.API_BUILD_URL ?? "http://127.0.0.1:8000/api/v1";
const BROWSER_BASE: string = import.meta.env.PUBLIC_API_URL ?? "/api/v1";

export function apiBaseUrl(): string {
	// Astro ejecuta este cliente en dos contextos: Node durante el build y el
	// navegador después de hidratar la isla. La ruta relativa del navegador
	// permite que el proxy de Vite resuelva CORS sin exponer una URL absoluta.
	return typeof window === "undefined" ? BUILD_BASE : BROWSER_BASE;
}

interface RequestOptions extends Omit<RequestInit, "headers"> {
	headers?: HeadersInit;
	/** Si está presente, se envía el header X-Participant-ID. */
	participantId?: string;
}

function classifyError(status: number, message?: string | null): ApiError {
	// Se traduce el contrato HTTP a códigos de dominio para que la UI pueda
	// decidir mensajes y reintentos sin acoplarse a cada status numérico.
	const code: ApiErrorCode =
		status === 400
			? "bad_request"
			: status === 404
				? "not_found"
				: status === 409
					? "conflict"
					: status >= 500
						? "server_error"
						: "unknown";
	return { code, status, message: message ?? "" };
}

async function request<T>(
	path: string,
	options: RequestOptions = {},
): Promise<ApiResult<T>> {
	// Todas las operaciones pasan por este punto para compartir headers,
	// manejo de red, parseo tolerante y el resultado discriminado `ok`.
	const { participantId, headers, ...init } = options;

	const requestHeaders = new Headers(headers);
	requestHeaders.set("Accept", "application/json");
	if (participantId !== undefined) {
		requestHeaders.set("X-Participant-ID", participantId);
	}

	let response: Response;
	try {
		response = await fetch(`${apiBaseUrl()}${path}`, {
			...init,
			headers: requestHeaders,
		});
	} catch {
		return {
			ok: false,
			error: {
				code: "network",
				status: null,
				message: "No se pudo conectar con la API.",
			},
		};
	}

	// 204 No Content y cuerpos vacíos se toleran según el contrato.
	const rawBody = await response.text();
	const payload: unknown = rawBody ? safeJsonParse(rawBody) : null;

	if (!response.ok) {
		const message = readErrorMessage(payload);
		return { ok: false, error: classifyError(response.status, message) };
	}

	// El backend usa 204 para DELETE; por eso no se fuerza JSON cuando el cuerpo
	// está vacío y se devuelve `null` de forma compatible con el contrato.
	// Éxito: colecciones responden { data, error }; el detalle de actividad
	// responde solamente { data }. Se aceptan ambas formas.
	const data =
		payload !== null &&
		typeof payload === "object" &&
		"data" in payload &&
		(payload as { data: unknown }).data !== undefined
			? (payload as { data: unknown }).data
			: payload;
	return { ok: true, data: data as T, status: response.status };
}

function safeJsonParse(raw: string): unknown {
	// Una respuesta no JSON no debe romper el flujo de errores: se conserva el
	// texto original para que el clasificador pueda devolver un fallo legible.
	try {
		return JSON.parse(raw);
	} catch {
		return raw;
	}
}

function readErrorMessage(payload: unknown): string | null {
	// Solo se lee `error` cuando realmente es texto; así se evita mostrar
	// objetos de validación como si fueran mensajes simples.
	if (
		payload !== null &&
		typeof payload === "object" &&
		"error" in payload &&
		typeof (payload as { error: unknown }).error === "string"
	) {
		return (payload as { error: string }).error;
	}
	return null;
}

/** GET /api/v1/activities/ — usado durante el build del listado. */
export function getActivities(): Promise<ApiResult<Activity[]>> {
	return request<Activity[]>("/activities/");
}

/** GET /api/v1/activities/{id}/ */
export function getActivity(id: string): Promise<ApiResult<Activity>> {
	return request<Activity>(`/activities/${id}/`);
}

/**
 * GET /api/v1/me/enrollments/
 * Requiere identidad de laboratorio vía X-Participant-ID.
 */
export function getMyEnrollments(
	participantId: string,
): Promise<ApiResult<Enrollment[]>> {
	return request<Enrollment[]>("/me/enrollments/", { participantId });
}

/**
 * PUT /api/v1/me/enrollments/{activity_id}/
 * Idempotente: 201 al crear, 200 si ya existía.
 */
export function enrollInActivity(
	activityId: string,
	participantId: string,
): Promise<ApiResult<Enrollment>> {
	return request<Enrollment>(`/me/enrollments/${activityId}/`, {
		method: "PUT",
		participantId,
	});
}

/**
 * DELETE /api/v1/me/enrollments/{activity_id}/cancel/
 * Responde 204 sin cuerpo cuando la cancelación tiene éxito.
 */
export function cancelEnrollment(
	activityId: string,
	participantId: string,
): Promise<ApiResult<null>> {
	return request<null>(`/me/enrollments/${activityId}/cancel/`, {
		method: "DELETE",
		participantId,
	});
}
