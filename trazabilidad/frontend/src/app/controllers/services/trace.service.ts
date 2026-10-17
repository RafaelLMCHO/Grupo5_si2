import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { PublicTraceResponse } from '../../models/trace.model';
import { environment } from '../../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class TraceService {
  private http = inject(HttpClient);
  private apiUrl = `${environment.apiUrl}/trace`;

  /** CU-022: consulta pública del historial de trazabilidad por UUID (sin autenticación). */
  getTrace(uuidpublico: string): Observable<PublicTraceResponse> {
    return this.http.get<PublicTraceResponse>(`${this.apiUrl}/${uuidpublico}`);
  }
}
