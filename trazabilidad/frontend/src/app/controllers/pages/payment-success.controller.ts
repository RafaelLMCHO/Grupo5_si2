import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterLink } from '@angular/router';

@Component({
  selector: 'app-payment-success',
  standalone: true,
  imports: [CommonModule, RouterLink],
  template: `
    <div class="payment-container">
      <div class="card success-card">
        <div class="icon-circle success-icon">
          <svg viewBox="0 0 24 24" width="48" height="48" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round">
            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
            <polyline points="22 4 12 14.01 9 11.01"></polyline>
          </svg>
        </div>
        <h2>¡Pago Procesado Exitosamente!</h2>
        <p class="subtitle">La transacción ha sido confirmada por Stripe y procesada por el sistema.</p>
        
        <div class="info-box">
          <p><strong>Estado:</strong> <span class="badge badge-success">Pagado / Completado</span></p>
          <p>El comprobante y los estados de trazabilidad han sido sincronizados en la plataforma.</p>
        </div>

        <div class="actions">
          <a routerLink="/sales" class="btn btn-primary">Volver a Ventas</a>
          <a routerLink="/dashboard" class="btn btn-secondary">Ir al Dashboard</a>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .payment-container {
      display: flex;
      justify-content: center;
      align-items: center;
      min-height: 70vh;
      padding: 2rem;
    }
    .card {
      background: #ffffff;
      border-radius: 12px;
      box-shadow: 0 10px 25px rgba(0,0,0,0.08);
      max-width: 520px;
      width: 100%;
      padding: 2.5rem;
      text-align: center;
    }
    .icon-circle {
      width: 80px;
      height: 80px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      margin: 0 auto 1.5rem;
    }
    .success-icon {
      background: #e8f5e9;
      color: #2e7d32;
    }
    h2 {
      color: #1a1a1a;
      margin-bottom: 0.5rem;
      font-size: 1.5rem;
    }
    .subtitle {
      color: #666;
      font-size: 0.95rem;
      margin-bottom: 1.5rem;
    }
    .info-box {
      background: #f8f9fa;
      border-radius: 8px;
      padding: 1rem 1.25rem;
      margin-bottom: 2rem;
      text-align: left;
      font-size: 0.9rem;
      border-left: 4px solid #2e7d32;
    }
    .badge-success {
      background: #2e7d32;
      color: white;
      padding: 0.2rem 0.6rem;
      border-radius: 4px;
      font-size: 0.8rem;
    }
    .actions {
      display: flex;
      gap: 1rem;
      justify-content: center;
    }
    .btn {
      padding: 0.75rem 1.5rem;
      border-radius: 6px;
      font-weight: 500;
      text-decoration: none;
      display: inline-block;
      transition: all 0.2s;
    }
    .btn-primary {
      background: #1976d2;
      color: white;
    }
    .btn-primary:hover {
      background: #1565c0;
    }
    .btn-secondary {
      background: #f1f3f4;
      color: #333;
    }
    .btn-secondary:hover {
      background: #e4e7ea;
    }
  `]
})
export class PaymentSuccessController implements OnInit {
  private route = inject(ActivatedRoute);
  sessionId = signal<string | null>(null);

  ngOnInit(): void {
    this.route.queryParams.subscribe(params => {
      this.sessionId.set(params['session_id'] || null);
    });
  }
}
