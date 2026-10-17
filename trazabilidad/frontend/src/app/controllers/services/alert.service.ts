import { Injectable, signal, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable, tap } from 'rxjs';
import {
  Alerta,
  AlertaListResponse,
  AlertaSummary,
  CreateAlertaRequest,
  UpdateAlertaEstadoRequest
} from '../../models/alert.model';
import { environment } from '../../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class AlertService {
  private http = inject(HttpClient);
  private apiUrl = `${environment.apiUrl}/alerts`;

  alertsSignal = signal<Alerta[]>([]);
  totalSignal = signal<number>(0);
  loadingSignal = signal<boolean>(false);

  getAlerts(
    estado: string = '',
    tipoalerta: string = '',
    gravedad: string = '',
    idunidad?: number,
    skip: number = 0,
    limit: number = 50
  ): Observable<AlertaListResponse> {
    this.loadingSignal.set(true);
    let params = new HttpParams().set('skip', skip.toString()).set('limit', limit.toString());
    if (estado) params = params.set('estado', estado);
    if (tipoalerta) params = params.set('tipoalerta', tipoalerta);
    if (gravedad) params = params.set('gravedad', gravedad);
    if (idunidad) params = params.set('idunidad', idunidad.toString());

    return this.http.get<AlertaListResponse>(this.apiUrl, { params }).pipe(
      tap({
        next: (res) => {
          this.alertsSignal.set(res.items);
          this.totalSignal.set(res.total);
          this.loadingSignal.set(false);
        },
        error: () => this.loadingSignal.set(false)
      })
    );
  }

  getSummary(): Observable<AlertaSummary> {
    return this.http.get<AlertaSummary>(`${this.apiUrl}/summary`);
  }

  getAlert(idalerta: number): Observable<Alerta> {
    return this.http.get<Alerta>(`${this.apiUrl}/${idalerta}`);
  }

  createAlert(data: CreateAlertaRequest): Observable<Alerta> {
    return this.http.post<Alerta>(this.apiUrl, data);
  }

  updateEstado(idalerta: number, data: UpdateAlertaEstadoRequest): Observable<Alerta> {
    return this.http.patch<Alerta>(`${this.apiUrl}/${idalerta}/estado`, data);
  }
}
