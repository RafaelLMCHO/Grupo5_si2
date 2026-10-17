import 'package:flutter/material.dart';
import '../controllers/alert_service.dart';

class ReportSuspicionView extends StatefulWidget {
  final String? uuidpublico;
  final String? numeroserie;

  const ReportSuspicionView({super.key, this.uuidpublico, this.numeroserie});

  @override
  State<ReportSuspicionView> createState() => _ReportSuspicionViewState();
}

class _ReportSuspicionViewState extends State<ReportSuspicionView> {
  static const _motivos = <String, String>{
    'producto_falso': 'Producto falsificado',
    'empaque_alterado': 'Empaque alterado o dañado',
    'serial_duplicado': 'Número de serie duplicado',
    'origen_dudoso': 'Origen o procedencia dudosa',
    'otro': 'Otro (describir abajo)',
  };

  final _formKey = GlobalKey<FormState>();
  final _descripcionController = TextEditingController();
  final _evidenciaController = TextEditingController();
  final _nombreController = TextEditingController();
  final _contactoController = TextEditingController();

  String _motivo = 'producto_falso';
  bool _enviando = false;

  @override
  void dispose() {
    _descripcionController.dispose();
    _evidenciaController.dispose();
    _nombreController.dispose();
    _contactoController.dispose();
    super.dispose();
  }

  Future<void> _enviar() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() => _enviando = true);
    try {
      final referencia = await AlertService.reportSuspicion(
        uuidpublico: widget.uuidpublico,
        numeroserie: widget.numeroserie,
        motivo: _motivo,
        descripcion: _descripcionController.text.trim(),
        evidencia: _evidenciaController.text.trim(),
        nombrereportante: _nombreController.text.trim(),
        contactoreportante: _contactoController.text.trim(),
      );
      if (!mounted) return;
      await showDialog(
        context: context,
        builder: (_) => AlertDialog(
          backgroundColor: const Color(0xFF1E293B),
          title: const Text('Reporte enviado', style: TextStyle(color: Colors.white)),
          content: Text(
            'Su reporte fue registrado con la referencia $referencia. '
            'El equipo de operaciones revisará la incidencia.',
            style: const TextStyle(color: Colors.white70),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(context).pop(),
              child: const Text('Entendido', style: TextStyle(color: Color(0xFF38BDF8))),
            ),
          ],
        ),
      );
      if (mounted) Navigator.of(context).pop(true);
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(e.toString().replaceAll('Exception: ', ''))),
      );
    } finally {
      if (mounted) setState(() => _enviando = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0F172A),
      appBar: AppBar(
        backgroundColor: const Color(0xFF1E293B),
        title: const Row(
          children: [
            Icon(Icons.report_rounded, color: Color(0xFFF87171)),
            SizedBox(width: 8),
            Text('Reportar Sospecha (CU-023)', style: TextStyle(fontSize: 17, color: Colors.white)),
          ],
        ),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(18),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              _infoUnidad(),
              const SizedBox(height: 18),
              const Text('Motivo de la sospecha',
                  style: TextStyle(color: Color(0xFF94A3B8), fontSize: 12)),
              const SizedBox(height: 6),
              DropdownButtonFormField<String>(
                initialValue: _motivo,
                dropdownColor: const Color(0xFF1E293B),
                decoration: _inputDecoration(),
                style: const TextStyle(color: Colors.white),
                items: _motivos.entries
                    .map((e) => DropdownMenuItem(value: e.key, child: Text(e.value)))
                    .toList(),
                onChanged: (v) => setState(() => _motivo = v ?? 'producto_falso'),
              ),
              const SizedBox(height: 14),
              TextFormField(
                controller: _descripcionController,
                maxLines: 3,
                style: const TextStyle(color: Colors.white),
                decoration: _inputDecoration(hint: 'Describa la irregularidad observada'),
              ),
              const SizedBox(height: 14),
              TextFormField(
                controller: _evidenciaController,
                style: const TextStyle(color: Colors.white),
                decoration: _inputDecoration(hint: 'URL o referencia de la evidencia'),
              ),
              const SizedBox(height: 14),
              TextFormField(
                controller: _nombreController,
                style: const TextStyle(color: Colors.white),
                decoration: _inputDecoration(hint: 'Su nombre (opcional)'),
              ),
              const SizedBox(height: 14),
              TextFormField(
                controller: _contactoController,
                style: const TextStyle(color: Colors.white),
                decoration: _inputDecoration(hint: 'Correo o teléfono de contacto (opcional)'),
              ),
              const SizedBox(height: 22),
              ElevatedButton.icon(
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFFDC2626),
                  padding: const EdgeInsets.symmetric(vertical: 15),
                ),
                onPressed: _enviando ? null : _enviar,
                icon: _enviando
                    ? const SizedBox(
                        width: 18, height: 18,
                        child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                      )
                    : const Icon(Icons.send, color: Colors.white),
                label: Text(_enviando ? 'Enviando...' : 'Enviar reporte',
                    style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
              ),
              const SizedBox(height: 10),
              const Text(
                'Puede reportar de forma anónima. La empresa propietaria de la unidad '
                'recibirá una alerta de autenticidad.',
                style: TextStyle(color: Colors.white38, fontSize: 11),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _infoUnidad() {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: const Color(0xFF1E293B),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: const Color(0xFF334155)),
      ),
      child: Row(
        children: [
          const Icon(Icons.qr_code_2, color: Color(0xFF38BDF8)),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                if (widget.numeroserie != null)
                  Text('Nº de serie: ${widget.numeroserie}',
                      style: const TextStyle(color: Colors.white, fontSize: 13)),
                if (widget.uuidpublico != null)
                  Text('UUID: ${widget.uuidpublico}',
                      style: const TextStyle(color: Color(0xFF94A3B8), fontSize: 11)),
                if (widget.uuidpublico == null && widget.numeroserie == null)
                  const Text('Unidad no identificada',
                      style: TextStyle(color: Color(0xFF94A3B8), fontSize: 12)),
              ],
            ),
          ),
        ],
      ),
    );
  }

  InputDecoration _inputDecoration({String? hint}) {
    return InputDecoration(
      hintText: hint,
      hintStyle: const TextStyle(color: Colors.white38),
      filled: true,
      fillColor: const Color(0xFF1E293B),
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(10),
        borderSide: const BorderSide(color: Color(0xFF334155)),
      ),
      enabledBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(10),
        borderSide: const BorderSide(color: Color(0xFF334155)),
      ),
    );
  }
}
