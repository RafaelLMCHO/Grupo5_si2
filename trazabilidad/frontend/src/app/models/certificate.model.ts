// Modelos de registros Blockchain y certificados (CU-034)

export interface RegistroBlockchain {
  idregistro: number;
  idevento: number;
  payloadhash: string;
  txhash?: string | null;
  blocknumber?: number | null;
  network?: string | null;
  chainid?: string | null;
  contractaddress?: string | null;
  fechaenvio?: string | null;
  fechaconfirmacion?: string | null;
  estado?: string | null;
  numeroconfirmaciones?: number | null;
  mensajeerror?: string | null;
}

export interface EventoCertificado {
  idevento: number;
  tipoevento: string;
  fechahora?: string | null;
  descripcion?: string | null;
  payloadhash?: string | null;
  estadoverificacion?: string | null;
  registro_blockchain?: RegistroBlockchain | null;
  en_blockchain: boolean;
  verificado: boolean;
}

export interface CertificacionUnidad {
  idcertificacion: number;
  nombre: string;
  entidademisora?: string | null;
  descripcion?: string | null;
  fechaobtencion?: string | null;
}

export interface DocumentoCertificado {
  iddocumento: number;
  nombre: string;
  tipodocumento: string;
  urlarchivo: string;
  hasharchivo: string;
  fechaemision: string;
  fechavencimiento?: string | null;
}

export interface UnitCertificateResponse {
  idunidad: number;
  numeroserie: string;
  uuidpublico: string;
  producto?: string | null;
  modelo?: string | null;
  sku?: string | null;
  color?: string | null;
  capacidad?: string | null;
  autenticidad: string;
  total_eventos: number;
  eventos: EventoCertificado[];
  certificaciones: CertificacionUnidad[];
  documentos: DocumentoCertificado[];
  registros_blockchain: number;
  registros_confirmados: number;
}

export interface DigitalCertificateResponse {
  idunidad: number;
  numeroserie: string;
  uuidpublico: string;
  producto?: string | null;
  sku?: string | null;
  codigocertificado: string;
  fechageneracion: string;
  hashcertificado: string;
  autenticidad: string;
  total_eventos: number;
  eventos_verificados: number;
  documentos: number;
  certificaciones: string[];
  emitido_por?: string | null;
  mensaje: string;
}
