import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { DigitalCertificateResponse, UnitCertificateResponse } from '../../models/certificate.model';
import { environment } from '../../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class CertificateService {
  private http = inject(HttpClient);
  private apiUrl = `${environment.apiUrl}/certificates`;

  getUnitCertificate(idunidad: number): Observable<UnitCertificateResponse> {
    return this.http.get<UnitCertificateResponse>(`${this.apiUrl}/units/${idunidad}`);
  }

  getDigitalCertificate(idunidad: number): Observable<DigitalCertificateResponse> {
    return this.http.get<DigitalCertificateResponse>(`${this.apiUrl}/units/${idunidad}/digital`);
  }

  getPublicCertificate(uuidpublico: string): Observable<UnitCertificateResponse> {
    return this.http.get<UnitCertificateResponse>(`${this.apiUrl}/public/${uuidpublico}`);
  }
}
