import 'package:flutter/material.dart';
import 'package:mobile_scanner/mobile_scanner.dart';
import '../controllers/trace_controller.dart';
import '../controllers/trace_service.dart';
import 'trace_history_view.dart';

class QrScannerView extends StatefulWidget {
  final TraceController traceController;

  const QrScannerView({super.key, required this.traceController});

  @override
  State<QrScannerView> createState() => _QrScannerViewState();
}

class _QrScannerViewState extends State<QrScannerView> {
  final MobileScannerController _scannerController = MobileScannerController(
    detectionSpeed: DetectionSpeed.noDuplicates,
    formats: const [BarcodeFormat.qrCode],
  );

  bool _processed = false;

  @override
  void dispose() {
    _scannerController.dispose();
    super.dispose();
  }

  Future<void> _onDetect(BarcodeCapture capture) async {
    if (_processed) return;
    final raw = capture.barcodes
        .map((b) => b.rawValue)
        .firstWhere((v) => v != null && v.isNotEmpty, orElse: () => null);
    if (raw == null) return;

    final uuid = TraceService.extractUuid(raw);
    if (uuid == null) return;

    _processed = true;
    await _scannerController.stop();
    if (!mounted) return;

    await Navigator.of(context).push(
      MaterialPageRoute(
        builder: (_) => TraceHistoryView(
          controller: widget.traceController,
          initialUuid: uuid,
        ),
      ),
    );

    if (mounted) {
      _processed = false;
      await _scannerController.start();
    }
  }

  void _openManualEntry() {
    Navigator.of(context).push(
      MaterialPageRoute(
        builder: (_) => TraceHistoryView(controller: widget.traceController),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0F172A),
      appBar: AppBar(
        backgroundColor: const Color(0xFF1E293B),
        title: const Row(
          children: [
            Icon(Icons.qr_code_scanner, color: Color(0xFF38BDF8)),
            SizedBox(width: 8),
            Text('Escanear Código QR', style: TextStyle(fontSize: 18, color: Colors.white)),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.keyboard, color: Color(0xFF38BDF8)),
            tooltip: 'Ingresar UUID manualmente',
            onPressed: _openManualEntry,
          ),
        ],
      ),
      body: Column(
        children: [
          Expanded(
            child: Stack(
              alignment: Alignment.center,
              children: [
                MobileScanner(
                  controller: _scannerController,
                  onDetect: _onDetect,
                  errorBuilder: (context, error) => _buildCameraError(error),
                ),
                _buildScanOverlay(),
              ],
            ),
          ),
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(16),
            color: const Color(0xFF1E293B),
            child: Column(
              children: [
                const Text(
                  'Apunte la cámara al código QR de la unidad para consultar su historial de trazabilidad.',
                  textAlign: TextAlign.center,
                  style: TextStyle(color: Colors.white70, fontSize: 13),
                ),
                const SizedBox(height: 12),
                OutlinedButton.icon(
                  style: OutlinedButton.styleFrom(
                    side: const BorderSide(color: Color(0xFF38BDF8)),
                    padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 12),
                  ),
                  onPressed: _openManualEntry,
                  icon: const Icon(Icons.keyboard, color: Color(0xFF38BDF8), size: 18),
                  label: const Text('Ingresar UUID manualmente', style: TextStyle(color: Color(0xFF38BDF8))),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildScanOverlay() {
    return IgnorePointer(
      child: Container(
        width: 250,
        height: 250,
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(20),
          border: Border.all(color: const Color(0xFF38BDF8), width: 3),
        ),
      ),
    );
  }

  Widget _buildCameraError(MobileScannerException error) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(Icons.no_photography, color: Color(0xFFF87171), size: 48),
            const SizedBox(height: 12),
            Text(
              'No se pudo acceder a la cámara.\n${error.errorCode.name}',
              textAlign: TextAlign.center,
              style: const TextStyle(color: Colors.white70, fontSize: 13),
            ),
            const SizedBox(height: 12),
            ElevatedButton(
              style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFF0284C7)),
              onPressed: _openManualEntry,
              child: const Text('Ingresar UUID manualmente', style: TextStyle(color: Colors.white)),
            ),
          ],
        ),
      ),
    );
  }
}
