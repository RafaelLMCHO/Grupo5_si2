import { Injectable, signal, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable, tap } from 'rxjs';
import {
  CreateDocumentoRequest,
  Documento,
  DocumentoListResponse,
  VerifyDocumentoResponse
} from '../../models/document.model';
import { environment } from '../../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class DocumentService {
  private http = inject(HttpClient);
  private apiUrl = `${environment.apiUrl}/documents`;

  documentsSignal = signal<Documento[]>([]);
  totalSignal = signal<number>(0);
  loadingSignal = signal<boolean>(false);

  getDocuments(
    tipodocumento: string = '',
    idunidad?: number,
    skip: number = 0,
    limit: number = 50
  ): Observable<DocumentoListResponse> {
    this.loadingSignal.set(true);
    let params = new HttpParams().set('skip', skip.toString()).set('limit', limit.toString());
    if (tipodocumento) params = params.set('tipodocumento', tipodocumento);
    if (idunidad) params = params.set('idunidad', idunidad.toString());

    return this.http.get<DocumentoListResponse>(this.apiUrl, { params }).pipe(
      tap({
        next: (res) => {
          this.documentsSignal.set(res.items);
          this.totalSignal.set(res.total);
          this.loadingSignal.set(false);
        },
        error: () => this.loadingSignal.set(false)
      })
    );
  }

  getByUnidad(idunidad: number): Observable<DocumentoListResponse> {
    return this.http.get<DocumentoListResponse>(`${this.apiUrl}/units/${idunidad}`);
  }

  getDocument(iddocumento: number): Observable<Documento> {
    return this.http.get<Documento>(`${this.apiUrl}/${iddocumento}`);
  }

  attachDocument(idunidad: number, data: CreateDocumentoRequest): Observable<Documento> {
    return this.http.post<Documento>(`${this.apiUrl}/units/${idunidad}`, data);
  }

  verifyDocument(iddocumento: number, data: { hasharchivo?: string; contenido?: string }): Observable<VerifyDocumentoResponse> {
    return this.http.post<VerifyDocumentoResponse>(`${this.apiUrl}/${iddocumento}/verify`, data);
  }

  deleteDocument(iddocumento: number): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/${iddocumento}`);
  }
}
