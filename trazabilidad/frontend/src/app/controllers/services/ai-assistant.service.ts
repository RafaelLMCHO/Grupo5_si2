import { Injectable, inject, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, tap } from 'rxjs';
import { environment } from '../../../environments/environment';
import { VoiceReportResponse } from '../../models/ai-report.model';

@Injectable({
  providedIn: 'root'
})
export class AiAssistantService {
  private http = inject(HttpClient);
  private apiUrl = environment.apiUrl;

  currentReportSignal = signal<VoiceReportResponse | null>(null);
  isLoadingSignal = signal<boolean>(false);
  isListeningSignal = signal<boolean>(false);
  isPlayingAudioSignal = signal<boolean>(false);
  errorMessageSignal = signal<string | null>(null);

  private recognition: any = null;

  constructor() {
    this.initSpeechRecognition();
  }

  private initSpeechRecognition(): void {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (SpeechRecognition) {
      this.recognition = new SpeechRecognition();
      this.recognition.lang = 'es-ES';
      this.recognition.continuous = false;
      this.recognition.interimResults = false;

      this.recognition.onstart = () => {
        this.isListeningSignal.set(true);
        this.errorMessageSignal.set(null);
      };

      this.recognition.onend = () => {
        this.isListeningSignal.set(false);
      };

      this.recognition.onerror = (event: any) => {
        this.isListeningSignal.set(false);
        if (event.error === 'no-speech') {
          return;
        }
        if (event.error === 'network') {
          this.errorMessageSignal.set(
            'El navegador no pudo conectar con el servicio de reconocimiento de voz en la nube (común en Brave o con bloqueadores de privacidad). Puedes escribir tu consulta o pulsar una consulta sugerida.'
          );
        } else if (event.error === 'not-allowed') {
          this.errorMessageSignal.set(
            'Permiso de micrófono denegado en el navegador. Por favor permite el acceso al micrófono o escribe tu consulta abajo.'
          );
        } else {
          this.errorMessageSignal.set('Aviso de micrófono: ' + event.error + '. Puedes escribir tu consulta directamente.');
        }
      };
    }
  }

  startListening(onResult: (text: string) => void): void {
    if (!this.recognition) {
      this.errorMessageSignal.set('El navegador no soporta reconocimiento de voz nativo. Puedes escribir tu consulta.');
      return;
    }
    this.recognition.onresult = (event: any) => {
      const text = event.results[0][0].transcript;
      onResult(text);
    };
    try {
      this.recognition.start();
    } catch (_) {
      this.recognition.stop();
      this.recognition.start();
    }
  }

  stopListening(): void {
    if (this.recognition) {
      this.recognition.stop();
      this.isListeningSignal.set(false);
    }
  }

  generateVoiceReport(query: string, context: string = 'web_dashboard'): Observable<VoiceReportResponse> {
    this.isLoadingSignal.set(true);
    this.errorMessageSignal.set(null);

    return this.http.post<VoiceReportResponse>(`${this.apiUrl}/ai/voice-report`, { query, context }).pipe(
      tap({
        next: (res) => {
          this.currentReportSignal.set(res);
          this.isLoadingSignal.set(false);
          if (res.voice_summary) {
            this.speak(res.voice_summary);
          }
        },
        error: (err) => {
          this.isLoadingSignal.set(false);
          this.errorMessageSignal.set(err.error?.detail || 'Error al procesar el reporte con IA.');
        }
      })
    );
  }

  speak(text: string): void {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = 'es-ES';
      utterance.rate = 1.0;
      utterance.pitch = 1.0;

      utterance.onstart = () => this.isPlayingAudioSignal.set(true);
      utterance.onend = () => this.isPlayingAudioSignal.set(false);
      utterance.onerror = () => this.isPlayingAudioSignal.set(false);

      window.speechSynthesis.speak(utterance);
    }
  }

  stopSpeaking(): void {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      this.isPlayingAudioSignal.set(false);
    }
  }

  downloadReportFile(reportId: string, format: 'pdf' | 'excel'): void {
    const url = `${this.apiUrl}/ai/reports/${reportId}/export?format=${format}`;
    this.http.get(url, { responseType: 'blob' }).subscribe({
      next: (blob) => {
        const fileUrl = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = fileUrl;
        a.download = `reporte_ia_${reportId.substring(0, 8)}.${format === 'excel' ? 'xlsx' : 'pdf'}`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(fileUrl);
      },
      error: (err) => {
        alert('Error al descargar el archivo: ' + (err.error?.detail || 'Intente nuevamente'));
      }
    });
  }

  reset(): void {
    this.currentReportSignal.set(null);
    this.errorMessageSignal.set(null);
    this.isLoadingSignal.set(false);
    this.stopSpeaking();
    this.stopListening();
  }
}
