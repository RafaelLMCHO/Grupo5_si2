import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { AlertService } from '../services/alert.service';
import { UnitService } from '../services/unit.service';
import { Alerta, AlertaSummary, CreateAlertaRequest } from '../../models/alert.model';

@Component({
  selector: 'app-alert-management',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: '../../views/pages/alert-management.view.html',
  styleUrls: ['../../views/pages/alert-management.view.css']
})
export class AlertManagementController implements OnInit {
  private alertService = inject(AlertService);
  private unitService = inject(UnitService);

  alerts = this.alertService.alertsSignal;
  total = this.alertService.totalSignal;
  isLoading = this.alertService.loadingSignal;
  units = this.unitService.unitsSignal;

  summary = signal<AlertaSummary | null>(null);

  selectedEstado = signal<string>('');
  selectedTipo = signal<string>('');
  selectedGravedad = signal<string>('');
  selectedUnidad = signal<number | null>(null);

  isCreateModalOpen = signal<boolean>(false);
  isResolveModalOpen = signal<boolean>(false);
  selectedAlert = signal<Alerta | null>(null);
  isSaving = signal<boolean>(false);

  resolveEstado = signal<string>('en_proceso');
  resolveComentario = signal<string>('');

  createForm: CreateAlertaRequest = {
    tipoalerta: 'incidencia_operativa',
    descripcion: '',
    gravedad: 'media',
    idunidad: undefined
  };

  tipos = [
    { value: '', label: '-- Todos los tipos --' },
    { value: 'temperatura', label: 'Temperatura' },
    { value: 'humedad', label: 'Humedad' },
    { value: 'vibracion', label: 'Vibración' },
    { value: 'retraso_aduanero', label: 'Retraso Aduanero' },
    { value: 'fraude_autenticidad', label: 'Fraude de Autenticidad' },
    { value: 'inconsistencia_cadena', label: 'Inconsistencia de Cadena' },
    { value: 'incidencia_operativa', label: 'Incidencia Operativa' }
  ];

  gravedades = [
    { value: '', label: '-- Todas las gravedades --' },
    { value: 'baja', label: 'Baja' },
    { value: 'media', label: 'Media' },
    { value: 'alta', label: 'Alta' },
    { value: 'critica', label: 'Crítica' }
  ];

  estados = [
    { value: '', label: '-- Todos los estados --' },
    { value: 'pendiente', label: 'Pendiente' },
    { value: 'en_proceso', label: 'En Proceso' },
    { value: 'resuelta', label: 'Resuelta' }
  ];

  errorMessage = signal<string>('');
  successMessage = signal<string>('');

  ngOnInit(): void {
    this.loadAlerts();
    this.loadSummary();
    this.unitService.getUnits('', '', undefined, 0, 100).subscribe();
  }

  loadAlerts(): void {
    this.errorMessage.set('');
    this.alertService
      .getAlerts(
        this.selectedEstado(),
        this.selectedTipo(),
        this.selectedGravedad(),
        this.selectedUnidad() ?? undefined
      )
      .subscribe({
        error: (err) => this.errorMessage.set(err?.error?.detail || 'Error al cargar alertas.')
      });
  }

  loadSummary(): void {
    this.alertService.getSummary().subscribe({
      next: (res) => this.summary.set(res),
      error: () => this.summary.set(null)
    });
  }

  onFilter(): void {
    this.loadAlerts();
    this.loadSummary();
  }

  openCreateModal(): void {
    this.createForm = {
      tipoalerta: 'incidencia_operativa',
      descripcion: '',
      gravedad: 'media',
      idunidad: undefined
    };
    this.errorMessage.set('');
    this.isCreateModalOpen.set(true);
  }

  closeCreateModal(): void {
    this.isCreateModalOpen.set(false);
  }

  saveAlert(): void {
    if (!this.createForm.descripcion || this.createForm.descripcion.trim().length < 5) {
      this.errorMessage.set('La descripción debe tener al menos 5 caracteres.');
      return;
    }
    this.isSaving.set(true);
    const payload: CreateAlertaRequest = {
      tipoalerta: this.createForm.tipoalerta,
      descripcion: this.createForm.descripcion.trim(),
      gravedad: this.createForm.gravedad,
      idunidad: this.createForm.idunidad ? Number(this.createForm.idunidad) : undefined
    };
    this.alertService.createAlert(payload).subscribe({
      next: () => {
        this.isSaving.set(false);
        this.closeCreateModal();
        this.successMessage.set('Incidencia registrada correctamente.');
        this.onFilter();
        setTimeout(() => this.successMessage.set(''), 4000);
      },
      error: (err) => {
        this.isSaving.set(false);
        this.errorMessage.set(err?.error?.detail || 'Error al registrar la incidencia.');
      }
    });
  }

  openResolveModal(alerta: Alerta): void {
    this.selectedAlert.set(alerta);
    this.resolveEstado.set(alerta.estado === 'pendiente' ? 'en_proceso' : 'resuelta');
    this.resolveComentario.set('');
    this.errorMessage.set('');
    this.isResolveModalOpen.set(true);
  }

  closeResolveModal(): void {
    this.isResolveModalOpen.set(false);
    this.selectedAlert.set(null);
  }

  saveResolve(): void {
    const alerta = this.selectedAlert();
    if (!alerta) return;
    this.isSaving.set(true);
    this.alertService
      .updateEstado(alerta.idalerta, {
        estado: this.resolveEstado(),
        comentario: this.resolveComentario() || undefined
      })
      .subscribe({
        next: () => {
          this.isSaving.set(false);
          this.closeResolveModal();
          this.successMessage.set('Alerta clasificada/resuelta correctamente.');
          this.onFilter();
          setTimeout(() => this.successMessage.set(''), 4000);
        },
        error: (err) => {
          this.isSaving.set(false);
          this.errorMessage.set(err?.error?.detail || 'Error al actualizar la alerta.');
        }
      });
  }

  gravedadClass(gravedad: string): string {
    switch (gravedad) {
      case 'critica':
        return 'sev-critica';
      case 'alta':
        return 'sev-alta';
      case 'media':
        return 'sev-media';
      default:
        return 'sev-baja';
    }
  }

  estadoClass(estado: string): string {
    switch (estado) {
      case 'resuelta':
        return 'st-resuelta';
      case 'en_proceso':
        return 'st-proceso';
      default:
        return 'st-pendiente';
    }
  }

  etiquetaEstado(estado: string): string {
    const found = this.estados.find((e) => e.value === estado);
    return found ? found.label : estado;
  }
}
