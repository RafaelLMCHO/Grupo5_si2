import { Component, OnInit, inject, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { DocumentService } from '../services/document.service';
import { UnitService } from '../services/unit.service';
import { AuthService } from '../services/auth.service';
import { CreateDocumentoRequest, Documento, VerifyDocumentoResponse } from '../../models/document.model';

@Component({
  selector: 'app-document-management',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: '../../views/pages/document-management.view.html',
  styleUrls: ['../../views/pages/document-management.view.css']
})
export class DocumentManagementController implements OnInit {
  private documentService = inject(DocumentService);
  private unitService = inject(UnitService);
  private authService = inject(AuthService);
  private route = inject(ActivatedRoute);

  documents = this.documentService.documentsSignal;
  total = this.documentService.totalSignal;
  isLoading = this.documentService.loadingSignal;
  units = this.unitService.unitsSignal;

  selectedTipo = signal<string>('');
  selectedUnidad = signal<number | null>(null);

  currentPage = signal<number>(1);
  pageSize = signal<number>(20);

  totalPages = computed(() => Math.ceil((this.total() || 0) / this.pageSize()) || 1);
  startIndex = computed(() => {
    const t = this.total() || 0;
    if (t === 0) return 0;
    return (this.currentPage() - 1) * this.pageSize() + 1;
  });
  endIndex = computed(() => {
    const t = this.total() || 0;
    return Math.min(this.currentPage() * this.pageSize(), t);
  });

  unitSearch = signal<string>('');
  filteredUnits = computed(() => {
    const q = this.unitSearch().trim().toLowerCase();
    const list = this.units();
    if (!q) return list.slice(0, 50);
    return list.filter(u => 
      u.numeroserie.toLowerCase().includes(q) || 
      (u.imei1 && u.imei1.includes(q)) ||
      (u.variante?.sku && u.variante.sku.toLowerCase().includes(q))
    ).slice(0, 50);
  });

  onUnitSearch(query: string): void {
    this.unitSearch.set(query);
    if (query.trim().length >= 2) {
      this.unitService.getUnits(query.trim(), '', undefined, 0, 50).subscribe();
    }
  }

  isCreateModalOpen = signal<boolean>(false);
  isVerifyModalOpen = signal<boolean>(false);
  isSaving = signal<boolean>(false);

  selectedDocument = signal<Documento | null>(null);
  verifyResult = signal<VerifyDocumentoResponse | null>(null);
  verifyInput = signal<string>('');

  createForm: CreateDocumentoRequest = {
    nombre: '',
    urlarchivo: '',
    tipodocumento: 'factura_compra',
    fechaemision: '',
    fechavencimiento: '',
    contenido: ''
  };

  tipos = [
    { value: '', label: '-- Todos los tipos --' },
    { value: 'factura_compra', label: 'Factura de Compra' },
    { value: 'certificado_importacion', label: 'Certificado de Importación' },
    { value: 'comprobante_garantia', label: 'Comprobante de Garantía' },
    { value: 'certificado_autenticidad', label: 'Certificado de Autenticidad' },
    { value: 'informe_tecnico', label: 'Informe Técnico' }
  ];

  errorMessage = signal<string>('');
  successMessage = signal<string>('');

  canManageDocs(): boolean {
    const roles = this.authService.currentUser()?.roles || [];
    return roles.includes('SuperAdministrador') || roles.includes('AdministradorEmpresa') || roles.includes('GestorOperaciones');
  }

  ngOnInit(): void {
    const unidadParam = this.route.snapshot.queryParamMap.get('unidad');
    if (unidadParam) {
      this.selectedUnidad.set(Number(unidadParam));
    }
    this.unitService.getUnits('', '', undefined, 0, 100).subscribe();
    this.loadDocuments();
  }

  loadDocuments(): void {
    this.errorMessage.set('');
    const skip = (this.currentPage() - 1) * this.pageSize();
    this.documentService
      .getDocuments(this.selectedTipo(), this.selectedUnidad() ?? undefined, skip, this.pageSize())
      .subscribe({
        error: (err) => this.errorMessage.set(err?.error?.detail || 'Error al cargar documentos.')
      });
  }

  nextPage(): void {
    if (this.currentPage() < this.totalPages()) {
      this.currentPage.update(p => p + 1);
      this.loadDocuments();
    }
  }

  prevPage(): void {
    if (this.currentPage() > 1) {
      this.currentPage.update(p => p - 1);
      this.loadDocuments();
    }
  }

  onPageSizeChange(size: number): void {
    this.pageSize.set(size);
    this.currentPage.set(1);
    this.loadDocuments();
  }

  onFilter(): void {
    this.currentPage.set(1);
    this.loadDocuments();
  }

  openCreateModal(): void {
    this.createForm = {
      nombre: '',
      urlarchivo: '',
      tipodocumento: 'factura_compra',
      fechaemision: '',
      fechavencimiento: '',
      contenido: ''
    };
    this.errorMessage.set('');
    this.isCreateModalOpen.set(true);
  }

  closeCreateModal(): void {
    this.isCreateModalOpen.set(false);
  }

  saveDocument(): void {
    const idunidad = this.selectedUnidad();
    if (!idunidad) {
      this.errorMessage.set('Debe seleccionar una unidad para adjuntar el documento.');
      return;
    }
    if (!this.createForm.nombre.trim() || !this.createForm.urlarchivo.trim()) {
      this.errorMessage.set('El nombre y la URL del archivo son obligatorios.');
      return;
    }
    this.isSaving.set(true);
    const payload: CreateDocumentoRequest = {
      nombre: this.createForm.nombre.trim(),
      urlarchivo: this.createForm.urlarchivo.trim(),
      tipodocumento: this.createForm.tipodocumento,
      fechaemision: this.createForm.fechaemision || undefined,
      fechavencimiento: this.createForm.fechavencimiento || undefined,
      contenido: this.createForm.contenido?.trim() ? this.createForm.contenido.trim() : undefined
    };
    this.documentService.attachDocument(idunidad, payload).subscribe({
      next: () => {
        this.isSaving.set(false);
        this.closeCreateModal();
        this.successMessage.set('Documento adjuntado correctamente.');
        this.loadDocuments();
        setTimeout(() => this.successMessage.set(''), 4000);
      },
      error: (err) => {
        this.isSaving.set(false);
        this.errorMessage.set(err?.error?.detail || 'Error al adjuntar el documento.');
      }
    });
  }

  openVerifyModal(doc: Documento): void {
    this.selectedDocument.set(doc);
    this.verifyResult.set(null);
    this.verifyInput.set('');
    this.errorMessage.set('');
    this.isVerifyModalOpen.set(true);
  }

  closeVerifyModal(): void {
    this.isVerifyModalOpen.set(false);
    this.selectedDocument.set(null);
    this.verifyResult.set(null);
  }

  verifyDocument(): void {
    const doc = this.selectedDocument();
    if (!doc) return;
    if (!this.verifyInput().trim()) {
      this.errorMessage.set('Ingrese el hash o el contenido del documento a comparar.');
      return;
    }
    this.documentService
      .verifyDocument(doc.iddocumento, { hasharchivo: this.verifyInput().trim() })
      .subscribe({
        next: (res) => {
          this.verifyResult.set(res);
          this.errorMessage.set('');
        },
        error: (err) => this.errorMessage.set(err?.error?.detail || 'Error al verificar el documento.')
      });
  }

  deleteDocument(doc: Documento): void {
    if (!confirm(`¿Eliminar el documento '${doc.nombre}'?`)) return;
    this.documentService.deleteDocument(doc.iddocumento).subscribe({
      next: () => {
        this.successMessage.set('Documento eliminado.');
        this.loadDocuments();
        setTimeout(() => this.successMessage.set(''), 4000);
      },
      error: (err) => this.errorMessage.set(err?.error?.detail || 'Error al eliminar el documento.')
    });
  }

  tipoLabel(tipo: string): string {
    const found = this.tipos.find((t) => t.value === tipo);
    return found ? found.label : tipo;
  }
}
