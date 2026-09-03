/**
 * Contrato de la API TUDA (no se agregan ni alteran endpoints).
 * Documentación: API.md en la raíz del repositorio.
 */

export interface Activity {
  id: string;
  title: string;
  starts_at: string;
  capacity: number;
  available_slots: number;
}

export interface Participant {
  id: string;
  name: string;
}

export interface Enrollment {
  activity_id: string;
  enrolled_at: string;
}

/** Envoltorio estándar de la API: éxito con `error: null`, error con `data: null`. */
export interface ApiResponse<T> {
  data: T | null;
  error: string | null;
}

/** Colecciones paginadas como `/api/v1/activities/`. */
export type ApiCollectionResponse<T> = ApiResponse<T[]>;

/** Clasificación didáctica de los errores HTTP relevantes del contrato. */
export type ApiErrorCode =
  | "bad_request" /* 400 */
  | "not_found" /* 404 */
  | "conflict" /* 409 */
  | "server_error" /* 500+ */
  | "network" /* sin conexión con la API */
  | "unknown";

export interface ApiError {
  code: ApiErrorCode;
  /** Código HTTP recibido, o `null` si la falla fue de red. */
  status: number | null;
  message: string;
}

/** Resultado tipado para consumir `data` / `error` sin excepciones. */
export type ApiResult<T> =
  | { ok: true; data: T; status: number }
  | { ok: false; error: ApiError };
