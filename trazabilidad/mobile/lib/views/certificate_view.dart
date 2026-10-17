import 'package:flutter/material.dart';
import '../controllers/certificate_service.dart';
import '../models/certificate_model.dart';

class CertificateView extends StatefulWidget {
  final String uuidpublico;

  const CertificateView({super.key, required this.uuidpublico});

  @override
  State<CertificateView> createState() => _CertificateViewState();
}

class _CertificateViewState extends State<CertificateView> {
  bool _loading = true;
  String? _error;
  UnitCertificateModel? _certificate;

  @override
  void initState() {
    super.initState();
    _cargar();
  }

  Future<void> _cargar() async {
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final data = await CertificateService.fetchPublicCertificate(widget.uuidpublico);
      if (!mounted) return;
      setState(() {
        _certificate = data;
        _loading = false;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _error = e.toString().replaceAll('Exception: ', '');
        _loading = false;
      });
    }
  }

  String _formatearFecha(String? iso) {
    if (iso == null || iso.isEmpty) return '—';
    final dt = DateTime.tryParse(iso)?.toLocal();
    if (dt == null) return iso;
    String two(int n) => n.toString().padLeft(2, '0');
    return '${two(dt.day)}/${two(dt.month)}/${dt.year}';
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0F172A),
      appBar: AppBar(
        backgroundColor: const Color(0xFF1E293B),
        title: const Row(
          children: [
            Icon(Icons.workspace_premium, color: Color(0xFF38BDF8)),
            SizedBox(width: 8),
            Text('Certificado (CU-034)', style: TextStyle(fontSize: 17, color: Colors.white)),
          ],
        ),
      ),
      body: _buildBody(),
    );
  }

  Widget _buildBody() {
    if (_loading) {
      return const Center(child: CircularProgressIndicator(color: Color(0xFF38BDF8)));
    }
    if (_error != null) {
      return Center(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Icon(Icons.error_outline, color: Color(0xFFF87171), size: 42),
              const SizedBox(height: 12),
              Text(_error!, textAlign: TextAlign.center,
                  style: const TextStyle(color: Colors.white70)),
              const SizedBox(height: 16),
              OutlinedButton(onPressed: _cargar, child: const Text('Reintentar')),
            ],
          ),
        ),
      );
    }

    final cert = _certificate!;
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          _buildAuthenticity(cert),
          const SizedBox(height: 16),
          _buildUnit(cert),
          const SizedBox(height: 16),
          _buildBlockchainSummary(cert),
          const SizedBox(height: 16),
          if (cert.certificaciones.isNotEmpty) ...[
            _sectionTitle('Certificaciones técnicas'),
            ..._certificaciones(cert),
            const SizedBox(height: 16),
          ],
          _sectionTitle('Documentos adjuntos'),
          if (cert.documentos.isEmpty)
            const Text('Sin documentos adjuntos.', style: TextStyle(color: Colors.white54))
          else
            ...cert.documentos.map(_buildDocumento),
          const SizedBox(height: 16),
          _sectionTitle('Eventos registrados'),
          if (cert.eventos.isEmpty)
            const Text('Sin eventos registrados.', style: TextStyle(color: Colors.white54))
          else
            ...cert.eventos.map(_buildEvento),
        ],
      ),
    );
  }

  Widget _sectionTitle(String text) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Text(text,
          style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 16)),
    );
  }

  Widget _buildAuthenticity(UnitCertificateModel cert) {
    late final Color color;
    late final IconData icono;
    late final String titulo;
    late final String detalle;
    if (cert.verificado) {
      color = const Color(0xFF059669);
      icono = Icons.verified;
      titulo = 'Certificado verificado en Blockchain';
      detalle = 'Los eventos de la unidad están anclados y confirmados en la red.';
    } else if (cert.sinDatos) {
      color = const Color(0xFFF59E0B);
      icono = Icons.gpp_maybe;
      titulo = 'Sin registros de trazabilidad';
      detalle = 'La unidad no tiene eventos registrados todavía.';
    } else {
      color = const Color(0xFFF59E0B);
      icono = Icons.hourglass_top;
      titulo = 'Registros pendientes de confirmación';
      detalle = 'Los eventos están registrados; la confirmación en Blockchain está pendiente.';
    }

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
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildUnit(UnitCertificateModel cert) {
    final detalles = [cert.color, cert.capacidad].where((e) => e != null && e.isNotEmpty).join(' ');
    return Card(
      color: const Color(0xFF1E293B),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(18),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(cert.producto ?? 'Unidad',
                style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 18)),
            if (detalles.isNotEmpty)
              Text(detalles, style: const TextStyle(color: Color(0xFF94A3B8), fontSize: 13)),
            const Divider(color: Color(0xFF334155), height: 22),
            _infoRow('Nº de Serie', cert.numeroserie),
            if (cert.modelo != null) _infoRow('Modelo', cert.modelo!),
            if (cert.sku != null) _infoRow('SKU', cert.sku!),
          ],
        ),
      ),
    );
  }

  Widget _buildBlockchainSummary(UnitCertificateModel cert) {
    return Card(
      color: const Color(0xFF1E293B),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(18),
        child: Row(
          children: [
            Expanded(child: _stat('Eventos', '${cert.totalEventos}')),
            Expanded(child: _stat('Confirmados', '${cert.registrosConfirmados}')),
            Expanded(child: _stat('Certificaciones', '${cert.certificaciones.length}')),
            Expanded(child: _stat('Documentos', '${cert.documentos.length}')),
          ],
        ),
      ),
    );
  }

  Widget _stat(String label, String value) {
    return Column(
      children: [
        Text(value, style: const TextStyle(color: Color(0xFF38BDF8), fontWeight: FontWeight.bold, fontSize: 18)),
        const SizedBox(height: 2),
        Text(label, style: const TextStyle(color: Color(0xFF94A3B8), fontSize: 11), textAlign: TextAlign.center),
      ],
    );
  }

  List<Widget> _certificaciones(UnitCertificateModel cert) {
    return cert.certificaciones
        .map((c) => Card(
              color: const Color(0xFF1E293B),
              margin: const EdgeInsets.only(bottom: 8),
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
              child: ListTile(
                leading: const Icon(Icons.verified_user, color: Color(0xFF10B981)),
                title: Text(c.nombre, style: const TextStyle(color: Colors.white, fontSize: 14)),
                subtitle: Text(
                  [
                    if (c.entidademisora != null) c.entidademisora!,
                    if (c.fechaobtencion != null) _formatearFecha(c.fechaobtencion),
                  ].join(' · '),
                  style: const TextStyle(color: Color(0xFF94A3B8), fontSize: 12),
                ),
              ),
            ))
        .toList();
  }

  Widget _buildDocumento(CertificateDocumento doc) {
    return Card(
      color: const Color(0xFF1E293B),
      margin: const EdgeInsets.only(bottom: 8),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: ListTile(
        leading: const Icon(Icons.description, color: Color(0xFF7DD3FC)),
        title: Text(doc.nombre, style: const TextStyle(color: Colors.white, fontSize: 14)),
        subtitle: Text(
          '${doc.tipodocumento.replaceAll('_', ' ')} · ${_formatearFecha(doc.fechaemision)}',
          style: const TextStyle(color: Color(0xFF94A3B8), fontSize: 12),
        ),
        trailing: const Icon(Icons.lock_outline, color: Color(0xFF64748B), size: 18),
      ),
    );
  }

  Widget _buildEvento(CertificateEvento ev) {
    final color = ev.verificado ? const Color(0xFF10B981) : const Color(0xFFF59E0B);
    return Card(
      color: const Color(0xFF1E293B),
      margin: const EdgeInsets.only(bottom: 10),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
        side: BorderSide(color: color.withValues(alpha: 0.5)),
      ),
      child: Padding(
        padding: const EdgeInsets.all(14),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(ev.enBlockchain ? Icons.check_circle : Icons.hourglass_top, color: color, size: 20),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(ev.tipoevento.replaceAll('_', ' ').toUpperCase(),
                      style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 13)),
                ),
                Text(_formatearFecha(ev.fechahora),
                    style: const TextStyle(color: Colors.white54, fontSize: 11)),
              ],
            ),
            if (ev.descripcion != null && ev.descripcion!.isNotEmpty) ...[
              const SizedBox(height: 6),
              Text(ev.descripcion!, style: const TextStyle(color: Colors.white70, fontSize: 12)),
            ],
            if (ev.payloadhash != null) ...[
              const SizedBox(height: 6),
              Text('Hash: ${ev.payloadhash!.substring(0, 16)}...',
                  style: const TextStyle(color: Color(0xFF64748B), fontSize: 11)),
            ],
          ],
        ),
      ),
    );
  }

  Widget _infoRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 120,
            child: Text(label, style: const TextStyle(color: Color(0xFF94A3B8), fontSize: 12)),
          ),
          Expanded(
            child: Text(value,
                style: const TextStyle(color: Colors.white, fontSize: 13, fontWeight: FontWeight.w500)),
          ),
        ],
      ),
    );
  }
}
