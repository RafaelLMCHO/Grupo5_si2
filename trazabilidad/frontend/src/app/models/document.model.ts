// Modelos de documentos adjuntos a unidades (CU-032)

export interface Documento {
  iddocumento: number;
  idunidad: number;
  nombre: string;
  urlarchivo: string;
  hasharchivo: string;
  fechaemision: string;
  fechavencimiento?: string | null;
  tipodocumento: string;
  numeroserie?: string | null;
  uuidpublico?: string | null;
  vencido?: boolean | null;
}

export interface DocumentoListResponse {
  total: number;
  items: Documento[];
}

export interface CreateDocumentoRequest {
  nombre: string;
  urlarchivo: string;
  tipodocumento: string;
  fechaemision?: string;
  fechavencimiento?: string;
  hasharchivo?: string;
  contenido?: string;
}

export interface VerifyDocumentoResponse {
  iddocumento: number;
  hasharchivo: string;
  hashcalculado: string;
  coincide: boolean;
  mensaje: string;
}
