import { useCallback, useEffect, useState } from "react";
import {
  cancelEnrollment,
  enrollInActivity,
  getMyEnrollments,
} from "../lib/api";
import { formatDateTime } from "../lib/format";
import type { ApiError, Enrollment } from "../types/activity";

const STORAGE_KEY = "tuda.participant-id";
const UUID_PATTERN =
  /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

type Phase = "waiting" | "loading" | "enrolled" | "not-enrolled" | "error";
type Action = "query" | "enroll" | "cancel" | null;

interface Props {
  activityId: string;
}

function resolveErrorMessage(error: ApiError): string {
  switch (error.code) {
    case "bad_request":
      return "No se pudo identificar al participante.";
    case "not_found":
      return "La actividad ya no existe.";
    case "conflict":
      return "La actividad no tiene cupos disponibles.";
    case "network":
      return "No se pudo conectar con la API. Verificá que el backend esté corriendo en 127.0.0.1:8000.";
    case "server_error":
      return `El servidor falló (HTTP ${error.status}). Podés reintentar.`;
    default:
      return error.message || `Error inesperado${error.status !== null ? ` (HTTP ${error.status})` : ""}.`;
  }
}

function canRetry(error: ApiError | null): boolean {
  return (
    error?.code === "network" ||
    error?.code === "server_error" ||
    error?.code === "unknown"
  );
}

export default function EnrollmentPanel({ activityId }: Props) {
  const [participantId, setParticipantId] = useState<string | null>(null);
  const [draftId, setDraftId] = useState("");
  const [phase, setPhase] = useState<Phase>("waiting");
  const [enrollment, setEnrollment] = useState<Enrollment | null>(null);
  const [error, setError] = useState<ApiError | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [busy, setBusy] = useState<Action>(null);
  const [hydratedAt, setHydratedAt] = useState<string | null>(null);

  // Resuelve la identidad de laboratorio: localStorage o variable pública.
  useEffect(() => {
    const saved = localStorage.getItem(STORAGE_KEY);
    const resolved =
      saved ??
      (import.meta.env.PUBLIC_PARTICIPANT_ID as string | undefined) ??
      "";
    setParticipantId(resolved);
    setDraftId(resolved);
    setHydratedAt(new Date().toLocaleTimeString("es-AR", { hour12: false }));
  }, []);

  const queryEnrollment = useCallback(async (identity: string) => {
    if (!identity) return;
    setBusy("query");
    setError(null);
    setNotice(null);
    setPhase("loading");

    const result = await getMyEnrollments(identity);

    if (!result.ok) {
      setError(result.error);
      setPhase("error");
      setBusy(null);
      return;
    }

    const mine = result.data.find((item) => item.activity.id === activityId);
    setEnrollment(mine ?? null);
    setPhase(mine ? "enrolled" : "not-enrolled");
    setBusy(null);
  }, [activityId]);

  useEffect(() => {
    if (participantId !== null) void queryEnrollment(participantId);
  }, [participantId, queryEnrollment]);

  function handleSaveIdentity() {
    const trimmed = draftId.trim();
    if (!UUID_PATTERN.test(trimmed)) {
      setError({
        code: "unknown",
        status: null,
        message:
          "El identificador no tiene formato de UUID válido (8-4-4-4-12 caracteres hexadecimales).",
      });
      setPhase("error");
      return;
    }
    localStorage.setItem(STORAGE_KEY, trimmed);
    setParticipantId(trimmed);
  }

  async function handleEnroll() {
    if (!participantId) return;
    setBusy("enroll");
    setError(null);
    setNotice(null);

    const result = await enrollInActivity(activityId, participantId);

    if (!result.ok) {
      setError(result.error);
      if (
        result.error.code === "network" ||
        result.error.code === "server_error"
      ) {
        setPhase("error");
      }
      setBusy(null);
      return;
    }

    setEnrollment(result.data);
    setPhase("enrolled");
    setNotice(
      result.status === 201
        ? "Inscripción creada (HTTP 201)."
        : "Ya estabas inscripto: la API confirmó la inscripción existente (HTTP 200).",
    );
    setBusy(null);
  }

  async function handleCancel() {
    if (!participantId) return;
    setBusy("cancel");
    setError(null);
    setNotice(null);

    const result = await cancelEnrollment(activityId, participantId);

    if (!result.ok) {
      setError(result.error);
      setBusy(null);
      return;
    }

    setEnrollment(null);
    setPhase("not-enrolled");
    setNotice("Inscripción cancelada (HTTP 204).");
    setBusy(null);
  }

  const isQuerying = busy === "query";
  const working = busy !== null;
  const dotTone = working
    ? "busy"
    : phase === "enrolled"
      ? "ok"
      : phase === "error"
        ? "error"
        : "idle";

  const statusText =
    phase === "waiting"
      ? "Estado de inscripción: esperando consulta del navegador"
      : phase === "loading" || isQuerying
        ? "Consultando inscripción..."
        : phase === "enrolled"
          ? "Estás inscripto en esta actividad."
          : phase === "not-enrolled"
            ? "No estás inscripto: quedan cupos para sumarte."
            : "No se pudo determinar el estado de inscripción.";

  return (
    <section
      className="layer layer--client"
      aria-label="Estado de inscripción consultado en el navegador"
      aria-busy={isQuerying}
    >
      <span className="layer__tag">Cliente · estado en tiempo real</span>

      <p className="layer__hint">
        Esta zona no existía en el HTML del build: aparece cuando React hidrata
        el componente y consulta <code>GET /me/enrollments/</code> desde tu
        navegador.
        {hydratedAt !== null && (
          <span className="js-indicator">
            <span className="status-dot status-dot--busy" aria-hidden="true" />
            JavaScript activo desde las {hydratedAt}
          </span>
        )}
      </p>

      <div className="island-grid">
        <div>
          <p className="status-line" aria-live="polite">
            <span
              className={`status-dot status-dot--${dotTone}`}
              aria-hidden="true"
            />
            <span className="status-text">{statusText}</span>
          </p>

          {/* Estado inicial visible también sin JavaScript */}
          {phase === "waiting" && (
            <p className="layer__hint">Estado dinámico pendiente de consulta</p>
          )}

          {notice !== null && error === null && !working && (
            <p className="alert alert--success" role="status">
              <span aria-hidden="true">✓</span>
              <span>{notice}</span>
            </p>
          )}

          {error !== null && (
            <div className="alert alert--error" role="alert">
              <span aria-hidden="true">✕</span>
              <span>{resolveErrorMessage(error)}</span>
            </div>
          )}

          {error !== null && error.code === "bad_request" && (
            <p className="layer__hint">
              Revisá el UUID en el panel de identidad y volvé a guardar.
            </p>
          )}

          {canRetry(error) && (
            <button
              type="button"
              className="btn btn--ghost"
              onClick={() => void queryEnrollment(participantId ?? "")}
              disabled={participantId === null || working}
            >
              Reintentar
            </button>
          )}

          {enrollment !== null && (
            <div className="enrolled-summary">
              <strong>Respuesta de la API</strong>
              <dl>
                <dt>Inscripto el</dt>
                <dd>{formatDateTime(enrollment.enrolled_at)}</dd>
                <dt>Participante</dt>
                <dd>{enrollment.participant.name}</dd>
                <dt>Actividad</dt>
                <dd>{enrollment.activity.title}</dd>
              </dl>
            </div>
          )}

          {phase === "enrolled" && (
            <div className="island-actions">
              <button
                type="button"
                className="btn btn--danger"
                onClick={() => void handleCancel()}
                disabled={working}
              >
                {busy === "cancel" ? "Cancelando..." : "Cancelar inscripción"}
              </button>
            </div>
          )}

          {phase === "not-enrolled" && (
            <div className="island-actions">
              <button
                type="button"
                className="btn"
                onClick={() => void handleEnroll()}
                disabled={working}
              >
                {busy === "enroll" ? "Procesando inscripción..." : "Inscribirme"}
              </button>
            </div>
          )}
        </div>

        <aside className="island-identity" aria-labelledby="identity-heading">
          <h3 id="identity-heading">Identidad de laboratorio</h3>
          <p className="layer__hint">
            La API no tiene login: tu identidad viaja en el header{" "}
            <code>X-Participant-ID</code>. Es un atajo didáctico, no una sesión
            real.
          </p>
          <div className="field">
            <label htmlFor="participant-id-input">UUID del participante</label>
            <input
              id="participant-id-input"
              className="input"
              type="text"
              value={draftId}
              onChange={(event) => setDraftId(event.target.value)}
              placeholder="bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"
              spellCheck={false}
              autoComplete="off"
            />
          </div>
          <div className="island-actions">
            <button
              type="button"
              className="btn btn--ghost"
              onClick={handleSaveIdentity}
              disabled={draftId.trim() === participantId}
            >
              {participantId ? "Cambiar de participante" : "Guardar identidad"}
            </button>
          </div>
          {participantId !== null && participantId !== "" && (
            <p className="layer__hint">
              Activa: <code>{participantId}</code> (guardada en localStorage)
            </p>
          )}
        </aside>
      </div>
    </section>
  );
}
