import { Component, signal, Signal, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { AuthService } from '../services/auth.service';
import { TenantService } from '../services/tenant.service';
import { AiAssistantService } from '../services/ai-assistant.service';
import { User } from '../../models/auth.models';
import { AnalyticsPanelController } from './analytics-panel.controller';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, RouterLink, FormsModule, AnalyticsPanelController],
  templateUrl: '../../views/pages/dashboard.view.html',
  styleUrls: ['../../views/pages/dashboard.view.scss']
})
export class DashboardController implements OnInit {
  private authService = inject(AuthService);
  private tenantService = inject(TenantService);
  aiService = inject(AiAssistantService);

  currentUser: Signal<User | null> = this.authService.currentUser;
  isLoading = signal(false);
  tenants = this.tenantService.tenantsSignal;

  showAiModal = signal(false);
  queryInput = '';
  quickPrompts = [
    '🏆 Top 10 productos más vendidos en el último trimestre',
    '📈 Top 5 por ingresos en los últimos 6 meses',
    '💰 Top 5 productos con mayor margen de ganancia',
    '🛠️ Tasa de devoluciones y garantías de los últimos 6 meses',
    '🔗 Unidades notarizadas en blockchain y alertas de sospecha',
    '🛒 Compras de los últimos 3 meses',
    '🚚 Envíos recientes y telemetría IoT',
    '📦 Stock disponible de iPhones',
    '🛡️ Resumen de bitácora y auditoría'
  ];

  isSuperAdmin(): boolean {
    const user = this.currentUser();
    if (!user) return false;
    return (user.roles || []).some(r => r.toLowerCase() === 'superadministrador');
  }

  get activePrompts(): string[] {
    if (this.isSuperAdmin()) {
      return [
        '🏢 Comparativa de ventas e ingresos entre todas las empresas',
        '📊 Ranking de stock y rotación de inventario en la red',
        '🚨 Comparación de incidencias y garantías por empresa',
        '📈 Participación de mercado entre todas las empresas',
        ...this.quickPrompts
      ];
    }
    return this.quickPrompts;
  }

  ngOnInit(): void {
    this.tenantService.getTenants().subscribe();
  }

  toggleAiModal(): void {
    this.showAiModal.update((v) => !v);
  }

  onStartVoice(): void {
    this.aiService.startListening((text) => {
      this.queryInput = text;
      this.onSubmitQuery(text);
    });
  }

  onStopVoice(): void {
    this.aiService.stopListening();
  }

  onSubmitQuery(text?: string): void {
    const q = (text !== undefined ? text : this.queryInput).trim();
    if (!q) return;
    this.queryInput = q;
    this.aiService.generateVoiceReport(q).subscribe();
  }

  onSelectPrompt(prompt: string): void {
    this.queryInput = prompt;
    this.onSubmitQuery(prompt);
  }

  onDownload(reportId: string, format: 'pdf' | 'excel'): void {
    this.aiService.downloadReportFile(reportId, format);
  }

  onTenantChange(event: Event): void {
    const selectElem = event.target as HTMLSelectElement;
    const tenantId = Number(selectElem.value);
    if (tenantId) {
      this.isLoading.set(true);
      this.authService.switchTenant(tenantId).subscribe({
        next: () => {
          this.isLoading.set(false);
          window.location.reload();
        },
        error: (err) => {
          this.isLoading.set(false);
          alert('Error al cambiar de empresa: ' + (err.error?.detail || 'Intente nuevamente'));
        }
      });
    }
  }

  onLogout(): void {
    this.authService.logout();
  }

  // El superadministrador puede estar viendo el contexto de otro tenant.
  analyticsTenantId(): number | undefined {
    const roles = this.currentUser()?.roles || [];
    if (!roles.includes('SuperAdministrador')) return undefined;
    const id = this.currentUser()?.tenant?.idtenant ?? this.currentUser()?.tenant_id;
    return id === undefined || id === null || id === '' ? undefined : Number(id);
  }

  canAccess(module: string): boolean {
    const roles = this.currentUser()?.roles || [];
    if (roles.includes('SuperAdministrador')) {
      const saasControlPlaneModules = [
        'tenants',
        'users',
        'roles',
        'subscription-plans',
        'subscriptions',
        'bitacora',
        'categories',
        'products',
        'certifications',
        'quotas',
        'billing'
      ];
      return saasControlPlaneModules.includes(module);
    }

    switch (module) {
      case 'tenants':
        return false;

      case 'users':
      case 'roles':
        return roles.includes('AdministradorEmpresa');

      case 'bitacora':
        return roles.includes('AdministradorEmpresa') || roles.includes('Auditor');

      case 'categories':
      case 'certifications':
      case 'actors':
      case 'locations':
      case 'receptions':
        return roles.includes('AdministradorEmpresa') || roles.includes('GestorOperaciones');

      case 'products':
      case 'tenant-catalog':
      case 'units':
      case 'qr-codes':
        return (
          roles.includes('AdministradorEmpresa') ||
          roles.includes('GestorOperaciones') ||
          roles.includes('GestorVentasPostventa') ||
          roles.includes('Auditor')
        );

      case 'purchases':
        return (
          roles.includes('AdministradorEmpresa') ||
          roles.includes('GestorOperaciones') ||
          roles.includes('GestorVentasPostventa')
        );

      case 'shipments':
        return (
          roles.includes('AdministradorEmpresa') ||
          roles.includes('GestorOperaciones') ||
          roles.includes('Auditor')
        );

      case 'alerts':
        return (
          roles.includes('AdministradorEmpresa') ||
          roles.includes('GestorOperaciones')
        );

      case 'documents':
        return (
          roles.includes('AdministradorEmpresa') ||
          roles.includes('GestorOperaciones') ||
          roles.includes('GestorVentasPostventa') ||
          roles.includes('Auditor')
        );

      case 'certificates':
        return (
          roles.includes('AdministradorEmpresa') ||
          roles.includes('GestorOperaciones') ||
          roles.includes('Auditor')
        );

      case 'sales':
      case 'post-sales':
        return roles.includes('AdministradorEmpresa') || roles.includes('GestorVentasPostventa');

      case 'reports':
      case 'quotas':
        return (
          roles.includes('AdministradorEmpresa') ||
          roles.includes('GestorOperaciones') ||
          roles.includes('GestorVentasPostventa') ||
          roles.includes('Auditor')
        );

      case 'billing':
        return roles.includes('AdministradorEmpresa');

      case 'traceability':
        return true;

      default:
        return false;
    }
  }

  // Helpers para renderizado gráfico SVG / Barras en reportes dinámicos
  getChartBars(chart: any): Array<{ label: string; value: number; barPct: number; pct: number; color: string; formatted: string }> {
    if (!chart || !chart.labels || !chart.datasets || !chart.datasets[0]) return [];
    const labels = chart.labels;
    const data: number[] = chart.datasets[0].data || [];
    const rawColors = chart.datasets[0].backgroundColor;
    const defaultPalette = ['#38bdf8', '#10b981', '#f59e0b', '#818cf8', '#ec4899', '#06b6d4', '#14b8a6', '#f97316'];
    const maxVal = Math.max(...data.map(v => Number(v) || 0), 1);
    const sumVal = data.reduce((acc, curr) => acc + (Number(curr) || 0), 0) || 1;

    return labels.map((lbl: string, idx: number) => {
      const val = Number(data[idx]) || 0;
      const color = Array.isArray(rawColors)
        ? (rawColors[idx] || defaultPalette[idx % defaultPalette.length])
        : (rawColors || defaultPalette[idx % defaultPalette.length]);
      const barPct = Math.max(3, Math.round((val / maxVal) * 100));
      const pct = Math.round((val / sumVal) * 100);
      let formatted = val.toLocaleString();
      const titleLower = (chart.title || '').toLowerCase();
      if (titleLower.includes('usd') || titleLower.includes('ingreso') || titleLower.includes('margen') || titleLower.includes('monto') || titleLower.includes('beneficio')) {
        formatted = `$${val.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
      } else if (titleLower.includes('°c') || titleLower.includes('temperatura')) {
        formatted = `${val.toFixed(1)} °C`;
      } else if (titleLower.includes('%') || titleLower.includes('tasa')) {
        formatted = `${val}%`;
      }
      return {
        label: lbl,
        value: val,
        barPct,
        pct,
        color,
        formatted
      };
    });
  }

  getDonutSegments(chart: any): Array<{ label: string; value: number; pct: number; strokeDasharray: string; strokeDashoffset: number; color: string }> {
    const bars = this.getChartBars(chart);
    if (!bars.length) return [];
    const circumference = 251.32; // 2 * pi * 40
    let accumulated = 0;
    return bars.map(b => {
      const segLength = (b.pct / 100) * circumference;
      const offset = -accumulated;
      accumulated += segLength;
      return {
        label: b.label,
        value: b.value,
        pct: b.pct,
        strokeDasharray: `${segLength} ${circumference - segLength}`,
        strokeDashoffset: offset,
        color: b.color
      };
    });
  }

  getLineChartData(chart: any): { path: string; area: string; points: Array<{ x: number; y: number; label: string; val: number }> } {
    const rawData = chart?.datasets?.[0]?.data || [];
    const labels: string[] = chart?.labels || [];
    const data: number[] = rawData.map((v: any) => Number(v) || 0);
    if (!data.length) return { path: '', area: '', points: [] };
    const minVal = Math.min(...data);
    const maxVal = Math.max(...data);
    const range = (maxVal - minVal) || 1;
    const width = 500;
    const height = 120;
    const padding = 20;

    const points = data.map((val, idx) => {
      const x = padding + (idx / Math.max(data.length - 1, 1)) * (width - 2 * padding);
      const y = height - padding - ((val - minVal) / range) * (height - 2 * padding);
      return { x, y, label: labels[idx] || '', val };
    });

    const path = points.map((p, idx) => `${idx === 0 ? 'M' : 'L'} ${p.x.toFixed(1)} ${p.y.toFixed(1)}`).join(' ');
    const area = `${path} L ${points[points.length - 1].x.toFixed(1)} ${height - 5} L ${points[0].x.toFixed(1)} ${height - 5} Z`;
    return { path, area, points };
  }
}
