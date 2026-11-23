import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-payment-cancel',
  standalone: true,
  imports: [CommonModule, RouterLink],
  template: `
    <div class="payment-container">
      <div class="card cancel-card">
        <div class="icon-circle cancel-icon">
          <svg viewBox="0 0 24 24" width="48" height="48" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="10"></circle>
            <line x1="15" y1="9" x2="9" y2="15"></line>
            <line x1="9" y1="9" x2="15" y2="15"></line>
          </svg>
        </div>
        <h2>Pago Cancelado</h2>
        <p class="subtitle">La sesión de pago en Stripe ha sido cancelada o expiró. No se ha realizado ningún cobro en su tarjeta.</p>
        
        <div class="info-box">
          <p><strong>Estado:</strong> <span class="badge badge-warning">Cancelado / Pendiente</span></p>
          <p>La orden de venta permanece abierta en su cuenta para cuando desee reintentar el pago.</p>
        </div>

        <div class="actions">
          <a routerLink="/sales" class="btn btn-primary">Volver a Intentar en Ventas</a>
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
    .cancel-icon {
      background: #ffebee;
      color: #c62828;
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
      background: #fff8e1;
      border-radius: 8px;
      padding: 1rem 1.25rem;
      margin-bottom: 2rem;
      text-align: left;
      font-size: 0.9rem;
      border-left: 4px solid #f57f17;
    }
    .badge-warning {
      background: #f57f17;
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
export class PaymentCancelController {}
