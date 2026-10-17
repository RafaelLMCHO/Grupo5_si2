import 'package:flutter/material.dart';
import '../controllers/trace_controller.dart';
import '../models/trace_history_model.dart';
import 'certificate_view.dart';
import 'report_suspicion_view.dart';

class TraceHistoryView extends StatefulWidget {
  final TraceController controller;
  final String? initialUuid;

  const TraceHistoryView({
    super.key,
    required this.controller,
    this.initialUuid,
  });

  @override
  State<TraceHistoryView> createState() => _TraceHistoryViewState();
}

class _TraceHistoryViewState extends State<TraceHistoryView> {
  final TextEditingController _inputController = TextEditingController();

  @override
  void initState() {
    super.initState();
    if (widget.initialUuid != null && widget.initialUuid!.isNotEmpty) {
      _inputController.text = widget.initialUuid!;
      widget.controller.load(widget.initialUuid!);
    }
  }

  @override
  void dispose() {
    _inputController.dispose();
    super.dispose();
  }

  String _formatearFecha(String? iso) {
    if (iso == null || iso.isEmpty) return '—';
    final dt = DateTime.tryParse(iso)?.toLocal();
    if (dt == null) return iso;
    String two(int n) => n.toString().padLeft(2, '0');
    return '${two(dt.day)}/${two(dt.month)}/${dt.year} ${two(dt.hour)}:${two(dt.minute)}';
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: widget.controller,
      builder: (context, _) {
        final ctrl = widget.controller;
        return Scaffold(
          backgroundColor: const Color(0xFF0F172A),
          appBar: AppBar(
            backgroundColor: const Color(0xFF1E293B),
            title: const Row(
              children: [
                Icon(Icons.timeline, color: Color(0xFF38BDF8)),
                SizedBox(width: 8),
                Text('Historial de Trazabilidad', style: TextStyle(fontSize: 18, color: Colors.white)),
              ],
            ),
          ),
          body: Column(
            children: [
              _buildSearchBar(ctrl),
              if (ctrl.errorMessage != null) _buildError(ctrl.errorMessage!),
              Expanded(child: _buildBody(ctrl)),
            ],
          ),
        );
      },
    );
  }

  Widget _buildSearchBar(TraceController ctrl) {
    return Container(
      padding: const EdgeInsets.all(12),
      color: const Color(0xFF1E293B),
      child: Row(
        children: [
          Expanded(
            child: TextField(
              controller: _inputController,
              style: const TextStyle(color: Colors.white),
              decoration: InputDecoration(
                hintText: 'UUID o URL del código QR',
                hintStyle: const TextStyle(color: Colors.white38),
                prefixIcon: const Icon(Icons.qr_code, color: Color(0xFF38BDF8)),
                filled: true,
                fillColor: const Color(0xFF0F172A),
                contentPadding: const EdgeInsets.symmetric(vertical: 0, horizontal: 16),
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(10),
                  borderSide: const BorderSide(color: Color(0xFF334155)),
                ),
              ),
              onSubmitted: (val) => ctrl.load(val),
            ),
          ),
          const SizedBox(width: 8),
          ElevatedButton(
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFF0284C7),
              padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 16),
            ),
            onPressed: () => ctrl.load(_inputController.text),
            child: const Icon(Icons.search, color: Colors.white),
          ),
        ],
      ),
    );
  }

  Widget _buildError(String message) {
    return Container(
      width: double.infinity,
      color: Colors.red.shade900,
      padding: const EdgeInsets.all(10),
      child: Text(message, style: const TextStyle(color: Colors.white, fontSize: 12)),
    );
  }

  Widget _buildBody(TraceController ctrl) {
    if (ctrl.isLoading) {
      return const Center(child: CircularProgressIndicator(color: Color(0xFF38BDF8)));
    }
    final trace = ctrl.trace;
    if (trace == null) {
      return const Center(
        child: Padding(
          padding: EdgeInsets.all(24.0),
          child: Text(
            'Escanee el código QR de una unidad o ingrese su UUID para consultar su historial verificable.',
            textAlign: TextAlign.center,
            style: TextStyle(color: Colors.white54, fontSize: 15),
          ),
        ),
      );
    }
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          _buildAuthenticityBanner(trace),
          const SizedBox(height: 16),
          _buildUnitCard(trace),
          const SizedBox(height: 12),
          _buildCertificateButton(trace),
          const SizedBox(height: 10),
          _buildReportButton(trace),
          const SizedBox(height: 16),
          const Text(
            'Historial de eventos',
            style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 16),
          ),
          const SizedBox(height: 8),
          if (trace.eventos.isEmpty)
            const Padding(
              padding: EdgeInsets.symmetric(vertical: 20),
              child: Text('Sin eventos registrados.', style: TextStyle(color: Colors.white54)),
            )
          else
            ...trace.eventos.map(_buildEventTile),
        ],
      ),
    );
  }

  Widget _buildAuthenticityBanner(TraceHistoryModel trace) {
    final autentico = trace.esAutentico;
    final color = autentico ? const Color(0xFF059669) : const Color(0xFFF59E0B);
    final icono = autentico ? Icons.verified : Icons.gpp_maybe;
    final titulo = autentico ? 'Producto auténtico y verificado' : 'Autenticidad no confirmada';
    final detalle = autentico
        ? 'Todos los eventos del historial están registrados y verificados.'
        : 'No se pudo confirmar la autenticidad de todos los eventos.';

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.15),
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: color, width: 1.4),
      ),
      child: Row(
        children: [
          Icon(icono, color: color, size: 36),
          const SizedBox(width: 14),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(titulo, style: TextStyle(color: color, fontWeight: FontWeight.bold, fontSize: 15)),
                const SizedBox(height: 4),
                Text(detalle, style: const TextStyle(color: Colors.white70, fontSize: 12)),
                const SizedBox(height: 4),
                Text(
                  'Eventos verificados: ${trace.eventosVerificados}/${trace.totalEventos}',
                  style: const TextStyle(color: Colors.white54, fontSize: 11),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildUnitCard(TraceHistoryModel trace) {
    return Card(
      color: const Color(0xFF1E293B),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(18.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              trace.producto?.nombre ?? 'Unidad',
              style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 18),
            ),
            if (trace.variante != null && trace.variante!.descripcion.isNotEmpty)
              Text(trace.variante!.descripcion, style: const TextStyle(color: Color(0xFF94A3B8), fontSize: 13)),
            const Divider(color: Color(0xFF334155), height: 22),
            _infoRow('Nº de Serie', trace.numeroserie),
            if (trace.empresa != null) _infoRow('Empresa', trace.empresa!),
            if (trace.estado != null) _infoRow('Estado', trace.estado!),
            if (trace.producto?.paisorigen != null) _infoRow('País de origen', trace.producto!.paisorigen!),
            if (trace.custodioActual != null) _infoRow('Custodio actual', trace.custodioActual!.nombre),
            if (trace.ubicacionActual != null)
              _infoRow('Ubicación actual', trace.ubicacionActual!.ubicacionCompleta),
            _infoRow('Fecha de ingreso', _formatearFecha(trace.fechaingreso)),
          ],
        ),
      ),
    );
  }

  Widget _buildCertificateButton(TraceHistoryModel trace) {
    return ElevatedButton.icon(
      style: ElevatedButton.styleFrom(
        backgroundColor: const Color(0xFF0284C7),
        padding: const EdgeInsets.symmetric(vertical: 14),
      ),
      icon: const Icon(Icons.workspace_premium, color: Colors.white),
      label: const Text(
        'Ver certificado y registros Blockchain',
        style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
      ),
      onPressed: () {
        Navigator.of(context).push(
          MaterialPageRoute(
            builder: (_) => CertificateView(uuidpublico: trace.uuidpublico),
          ),
        );
      },
    );
  }

  Widget _buildReportButton(TraceHistoryModel trace) {
    return OutlinedButton.icon(
      style: OutlinedButton.styleFrom(
        side: const BorderSide(color: Color(0xFFEF4444)),
        padding: const EdgeInsets.symmetric(vertical: 14),
      ),
      icon: const Icon(Icons.report_gmailerrorred_rounded, color: Color(0xFFF87171)),
      label: const Text(
        'Reportar sospecha de falsificación',
        style: TextStyle(color: Color(0xFFF87171), fontWeight: FontWeight.bold),
      ),
      onPressed: () {
        Navigator.of(context).push(
          MaterialPageRoute(
            builder: (_) => ReportSuspicionView(
              uuidpublico: trace.uuidpublico,
              numeroserie: trace.numeroserie,
            ),
          ),
        );
      },
    );
  }

  Widget _infoRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4.0),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 130,
            child: Text(label, style: const TextStyle(color: Color(0xFF94A3B8), fontSize: 12)),
          ),
          Expanded(
            child: Text(
              value,
              style: const TextStyle(color: Colors.white, fontSize: 13, fontWeight: FontWeight.w500),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildEventTile(TraceEventoInfo evento) {
    final verificado = evento.verificado;
    final color = verificado ? const Color(0xFF10B981) : const Color(0xFFF59E0B);
    return Card(
      color: const Color(0xFF1E293B),
      margin: const EdgeInsets.only(bottom: 10),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
        side: BorderSide(color: color.withValues(alpha: 0.5), width: 1),
      ),
      child: Padding(
        padding: const EdgeInsets.all(14.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(verificado ? Icons.check_circle : Icons.error_outline, color: color, size: 20),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    evento.tipoevento.replaceAll('_', ' ').toUpperCase(),
                    style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 13),
                  ),
                ),
                Text(
                  _formatearFecha(evento.fechahora),
                  style: const TextStyle(color: Colors.white54, fontSize: 11),
                ),
              ],
            ),
            if (evento.descripcion != null && evento.descripcion!.isNotEmpty) ...[
              const SizedBox(height: 6),
              Text(evento.descripcion!, style: const TextStyle(color: Colors.white70, fontSize: 12)),
            ],
            if (evento.ubicacion != null) ...[
              const SizedBox(height: 6),
              _iconLine(Icons.place, evento.ubicacion!.ubicacionCompleta),
            ],
            if (evento.actorOrigen != null)
              _iconLine(Icons.upload, 'Desde: ${evento.actorOrigen!.nombre}'),
            if (evento.actorDestino != null)
              _iconLine(Icons.download, 'Hacia: ${evento.actorDestino!.nombre}'),
          ],
        ),
      ),
    );
  }

  Widget _iconLine(IconData icon, String text) {
    return Padding(
      padding: const EdgeInsets.only(top: 4.0),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(icon, color: const Color(0xFF64748B), size: 14),
          const SizedBox(width: 6),
          Expanded(
            child: Text(text, style: const TextStyle(color: Color(0xFF94A3B8), fontSize: 12)),
          ),
        ],
      ),
    );
  }
}
