// Modelos de trazabilidad pública (CU-016/018/022)

export interface TraceActorInfo {
  nombre: string;
  tipo?: string | null;
}

export interface TraceUbicacionInfo {
  nombre: string;
  ciudad?: string | null;
  pais?: string | null;
}

export interface TraceEventoInfo {
  fechahora: string;
  tipoevento: string;
  descripcion?: string | null;
  estadoverificacion?: string | null;
  ubicacion?: TraceUbicacionInfo | null;
  actor_origen?: TraceActorInfo | null;
  actor_destino?: TraceActorInfo | null;
}

export interface TraceProductoInfo {
  nombre: string;
  paisorigen?: string | null;
  imagenurl?: string | null;
}

export interface TraceVarianteInfo {
  sku?: string | null;
  color?: string | null;
  capacidad?: string | null;
}

export interface PublicTraceResponse {
  uuidpublico: string;
  numeroserie: string;
  estado?: string | null;
  fechaingreso?: string | null;
  empresa?: string | null;
  producto?: TraceProductoInfo | null;
  variante?: TraceVarianteInfo | null;
  custodio_actual?: TraceActorInfo | null;
  ubicacion_actual?: TraceUbicacionInfo | null;
  qr_fechageneracion?: string | null;
  eventos: TraceEventoInfo[];
}
