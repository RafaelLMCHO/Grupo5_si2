import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { CertificateService } from '../services/certificate.service';
import { UnitService } from '../services/unit.service';
import { DigitalCertificateResponse, UnitCertificateResponse } from '../../models/certificate.model';

@Component({
  selector: 'app-certificate-management',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: '../../views/pages/certificate-management.view.html',
  styleUrls: ['../../views/pages/certificate-management.view.css']
})
export class CertificateManagementController implements OnInit {
  private certificateService = inject(CertificateService);
  private unitService = inject(UnitService);
  private route = inject(ActivatedRoute);

  units = this.unitService.unitsSignal;

  selectedUnidad = signal<number | null>(null);
  certificate = signal<UnitCertificateResponse | null>(null);
  digital = signal<DigitalCertificateResponse | null>(null);
  isLoading = signal<boolean>(false);

  activeTab = signal<'eventos' | 'certificaciones' | 'documentos'>('eventos');

  uuidLookup = signal<string>('');
  publicCertificate = signal<UnitCertificateResponse | null>(null);
  isLoadingPublic = signal<boolean>(false);

  errorMessage = signal<string>('');
  successMessage = signal<string>('');

  ngOnInit(): void {
    this.unitService.getUnits('', '', undefined, 0, 100).subscribe();
    const unidadParam = this.route.snapshot.queryParamMap.get('unidad');
    if (unidadParam) {
      this.selectedUnidad.set(Number(unidadParam));
      this.consultar();
    }
  }

  consultar(): void {
    const idunidad = this.selectedUnidad();
    if (!idunidad) {
      this.errorMessage.set('Debe seleccionar una unidad.');
      return;
    }
    this.errorMessage.set('');
    this.isLoading.set(true);
    this.certificate.set(null);
    this.digital.set(null);
    this.activeTab.set('eventos');
    this.certificateService.getUnitCertificate(idunidad).subscribe({
      next: (res) => {
        this.certificate.set(res);
        this.isLoading.set(false);
      },
      error: (err) => {
        this.isLoading.set(false);
        this.errorMessage.set(err?.error?.detail || 'Error al consultar el certificado.');
      }
    });
  }

  generarCertificadoDigital(): void {
    const idunidad = this.selectedUnidad();
    if (!idunidad) return;
    this.certificateService.getDigitalCertificate(idunidad).subscribe({
      next: (res) => {
        this.digital.set(res);
        this.successMessage.set('Certificado digital generado correctamente.');
        setTimeout(() => this.successMessage.set(''), 4000);
      },
      error: (err) => this.errorMessage.set(err?.error?.detail || 'Error al generar el certificado digital.')
    });
  }

  consultarPublico(): void {
    const uuid = this.uuidLookup().trim();
    if (!uuid) {
      this.errorMessage.set('Ingrese un UUID público.');
      return;
    }
    this.errorMessage.set('');
    this.isLoadingPublic.set(true);
    this.publicCertificate.set(null);
    this.certificateService.getPublicCertificate(uuid).subscribe({
      next: (res) => {
        this.publicCertificate.set(res);
        this.isLoadingPublic.set(false);
      },
      error: (err) => {
        this.isLoadingPublic.set(false);
        this.errorMessage.set(err?.error?.detail || 'Unidad no encontrada.');
      }
    });
  }

  imprimir(): void {
    window.print();
  }

  autenticidadClass(autenticidad: string): string {
    switch (autenticidad) {
      case 'verificado':
        return 'auth-verificado';
      case 'registrado':
        return 'auth-registrado';
      default:
        return 'auth-sin-datos';
    }
  }

  autenticidadLabel(autenticidad: string): string {
    switch (autenticidad) {
      case 'verificado':
        return 'Verificado en Blockchain';
      case 'registrado':
        return 'Registrado (sin anclaje confirmado)';
      default:
        return 'Sin datos de trazabilidad';
    }
  }
}
