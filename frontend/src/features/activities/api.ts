import type {
  Activity,
  CreateActivityPayload,
} from "@source/features/activities/types";

type ApiErrorResponse = {
  message?: string;
};

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(path, {
    headers: {
      "Content-Type": "application/json",
      ...init?.headers,
    },
    ...init,
  });

  if (!response.ok) {
    const body = (await response
      .json()
      .catch(() => null)) as ApiErrorResponse | null;
    throw new Error(body?.message ?? "No se pudo completar la solicitud.");
  }

  return response.json() as Promise<T>;
}

export function getActivities(): Promise<Activity[]> {
  return request<Activity[]>("/api/v2/activities/");
}

export function getActivity(activityId: string): Promise<Activity> {
  return request<Activity>(`/api/v2/activities/${activityId}/`);
}

export function createActivity(
  payload: CreateActivityPayload,
): Promise<Activity> {
  return request<Activity>("/api/v2/activities/", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}
