// Modelos de alertas e incidencias (CU-024)

export interface Alerta {
  idalerta: number;
  idtenant: number;
  idunidad?: number | null;
  idevento?: number | null;
  tipoalerta: string;
  descripcion: string;
  gravedad: string;
  fechadeteccion: string;
  fecharesolucion?: string | null;
  estado: string;
  idusuarioresolutor?: number | null;
  numeroserie?: string | null;
  uuidpublico?: string | null;
  usuarioresolutor_nombre?: string | null;
}

export interface AlertaListResponse {
  total: number;
  items: Alerta[];
}

export interface AlertaSummary {
  total: number;
  pendientes: number;
  en_proceso: number;
  resueltas: number;
  criticas: number;
  por_estado: Record<string, number>;
  por_gravedad: Record<string, number>;
  por_tipo: Record<string, number>;
}

export interface CreateAlertaRequest {
  tipoalerta: string;
  descripcion: string;
  gravedad: string;
  idunidad?: number;
  idevento?: number;
}

export interface UpdateAlertaEstadoRequest {
  estado: string;
  comentario?: string;
}
