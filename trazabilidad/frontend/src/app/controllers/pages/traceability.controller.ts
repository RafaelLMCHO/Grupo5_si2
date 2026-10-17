import { Component, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { TraceService } from '../services/trace.service';
import { CertificateService } from '../services/certificate.service';
import { PublicTraceResponse } from '../../models/trace.model';
import { UnitCertificateResponse } from '../../models/certificate.model';

@Component({
  selector: 'app-traceability',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: '../../views/pages/traceability.view.html',
  styleUrls: ['../../views/pages/traceability.view.css']
})
export class TraceabilityController {
  private traceService = inject(TraceService);
  private certificateService = inject(CertificateService);

  uuidInput = signal<string>('');
  trace = signal<PublicTraceResponse | null>(null);
  certificate = signal<UnitCertificateResponse | null>(null);
  isLoading = signal<boolean>(false);
  isLoadingCert = signal<boolean>(false);

  errorMessage = signal<string>('');

  consultar(): void {
    const uuid = this.uuidInput().trim();
    if (!uuid) {
      this.errorMessage.set('Ingrese el UUID público de la unidad.');
      return;
    }
    this.errorMessage.set('');
    this.isLoading.set(true);
    this.trace.set(null);
    this.certificate.set(null);
    this.traceService.getTrace(uuid).subscribe({
      next: (res) => {
        this.trace.set(res);
        this.isLoading.set(false);
      },
      error: (err) => {
        this.isLoading.set(false);
        this.errorMessage.set(err?.error?.detail || 'Unidad no encontrada.');
      }
    });
  }

  verCertificado(): void {
    const uuid = this.trace()?.uuidpublico;
    if (!uuid) return;
    this.isLoadingCert.set(true);
    this.certificateService.getPublicCertificate(uuid).subscribe({
      next: (res) => {
        this.certificate.set(res);
        this.isLoadingCert.set(false);
      },
      error: (err) => {
        this.isLoadingCert.set(false);
        this.errorMessage.set(err?.error?.detail || 'No se pudo cargar el certificado.');
      }
    });
  }

  autenticidad(): 'verificado' | 'registrado' | 'sin_datos' {
    const t = this.trace();
    if (!t || t.eventos.length === 0) return 'sin_datos';
    const verificado = t.eventos.some(
      (e) => (e.estadoverificacion || '').toLowerCase().includes('verific')
    );
    return verificado ? 'verificado' : 'registrado';
  }
}
