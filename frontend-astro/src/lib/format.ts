/** Formateo compartido entre páginas Astro y la isla React. */

const dateTimeFormat = new Intl.DateTimeFormat("es-AR", {
	dateStyle: "full",
	timeStyle: "short",
});

export function formatDateTime(isoDate: string): string {
	// Si la API entrega una fecha inválida, conservar el valor original ayuda a
	// detectar el problema sin dejar la interfaz sin información.
	const date = new Date(isoDate);
	if (Number.isNaN(date.getTime())) return isoDate;
	return dateTimeFormat.format(date);
}

export function formatSlots(available: number, capacity: number): string {
	return `${available} de ${capacity} cupos disponibles`;
}

export function availabilityLabel(activity: {
	available_slots: number;
	capacity: number;
}): { label: string; tone: "ok" | "low" | "full" } {
	// El orden importa: una actividad sin cupos debe prevalecer sobre el
	// umbral de "últimos cupos", incluso cuando la capacidad sea pequeña.
	if (activity.available_slots <= 0) {
		return { label: "Sin cupos", tone: "full" };
	}
	if (activity.available_slots <= Math.ceil(activity.capacity * 0.2)) {
		return { label: "Últimos cupos", tone: "low" };
	}
	return { label: "Disponible", tone: "ok" };
}
