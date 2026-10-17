import 'package:flutter/material.dart';
import '../controllers/alert_controller.dart';
import '../models/alert_model.dart';

class AlertsView extends StatefulWidget {
  final AlertController controller;

  const AlertsView({super.key, required this.controller});

  @override
  State<AlertsView> createState() => _AlertsViewState();
}

class _AlertsViewState extends State<AlertsView> {
  static const _filtros = <String, String>{
    'todas': 'Todas',
    'pendiente': 'Pendientes',
    'en_proceso': 'En proceso',
    'resuelta': 'Resueltas',
  };

  @override
  void initState() {
    super.initState();
    widget.controller.load();
  }

  Color _gravedadColor(String gravedad) {
    switch (gravedad) {
      case 'critica':
        return const Color(0xFFEF4444);
      case 'alta':
        return const Color(0xFFF59E0B);
      case 'media':
        return const Color(0xFF38BDF8);
      default:
        return const Color(0xFF94A3B8);
    }
  }

  Color _estadoColor(String estado) {
    switch (estado) {
      case 'resuelta':
        return const Color(0xFF10B981);
      case 'en_proceso':
        return const Color(0xFFF59E0B);
      default:
        return const Color(0xFFEF4444);
    }
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
    return Scaffold(
      backgroundColor: const Color(0xFF0F172A),
      appBar: AppBar(
        backgroundColor: const Color(0xFF1E293B),
        title: const Row(
          children: [
            Icon(Icons.warning_amber_rounded, color: Color(0xFFF59E0B)),
            SizedBox(width: 8),
            Text('Alertas e Incidencias', style: TextStyle(fontSize: 18, color: Colors.white)),
          ],
        ),
      ),
      body: ListenableBuilder(
        listenable: widget.controller,
        builder: (context, _) {
          final ctrl = widget.controller;
          return Column(
            children: [
              _buildFiltros(ctrl),
              if (ctrl.summary != null) _buildSummary(ctrl.summary!),
              if (ctrl.errorMessage != null) _buildError(ctrl.errorMessage!),
              Expanded(child: _buildLista(ctrl)),
            ],
          );
        },
      ),
    );
  }

  Widget _buildFiltros(AlertController ctrl) {
    return Container(
      color: const Color(0xFF1E293B),
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      child: SingleChildScrollView(
        scrollDirection: Axis.horizontal,
        child: Row(
          children: _filtros.entries.map((entry) {
            final key = entry.key;
            final seleccion = (ctrl.filtroEstado ?? 'todas') == key;
            return Padding(
              padding: const EdgeInsets.only(right: 8),
              child: ChoiceChip(
                label: Text(entry.value),
                selected: seleccion,
                onSelected: (_) => ctrl.load(estado: key == 'todas' ? null : key),
                selectedColor: const Color(0xFF0284C7),
                backgroundColor: const Color(0xFF0F172A),
                labelStyle: TextStyle(color: seleccion ? Colors.white : const Color(0xFF94A3B8)),
              ),
            );
          }).toList(),
        ),
      ),
    );
  }

  Widget _buildSummary(AlertSummary s) {
    Widget chip(String label, int value, Color color) {
      return Expanded(
        child: Container(
          margin: const EdgeInsets.symmetric(horizontal: 3),
          padding: const EdgeInsets.symmetric(vertical: 10),
          decoration: BoxDecoration(
            color: color.withValues(alpha: 0.15),
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: color.withValues(alpha: 0.5)),
          ),
          child: Column(
            children: [
              Text('$value', style: TextStyle(color: color, fontSize: 20, fontWeight: FontWeight.bold)),
              const SizedBox(height: 2),
              Text(label, style: const TextStyle(color: Color(0xFF94A3B8), fontSize: 11)),
            ],
          ),
        ),
      );
    }

    return Padding(
      padding: const EdgeInsets.all(12),
      child: Row(
        children: [
          chip('Pendientes', s.pendientes, const Color(0xFFEF4444)),
          chip('En proceso', s.enProceso, const Color(0xFFF59E0B)),
          chip('Resueltas', s.resueltas, const Color(0xFF10B981)),
          chip('Críticas', s.criticas, const Color(0xFFDC2626)),
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

  Widget _buildLista(AlertController ctrl) {
    if (ctrl.isLoading) {
      return const Center(child: CircularProgressIndicator(color: Color(0xFF38BDF8)));
    }
    if (ctrl.alerts.isEmpty) {
      return const Center(
        child: Text('No hay alertas para el filtro seleccionado.',
            style: TextStyle(color: Colors.white54)),
      );
    }
    return RefreshIndicator(
      onRefresh: () => ctrl.load(estado: ctrl.filtroEstado == 'todas' ? null : ctrl.filtroEstado),
      child: ListView.builder(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
        itemCount: ctrl.alerts.length,
        itemBuilder: (context, index) => _buildAlertaTile(ctrl.alerts[index]),
      ),
    );
  }

  Widget _buildAlertaTile(AlertModel alerta) {
    final gColor = _gravedadColor(alerta.gravedad);
    final eColor = _estadoColor(alerta.estado);
    return Card(
      color: const Color(0xFF1E293B),
      margin: const EdgeInsets.only(bottom: 10),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
        side: BorderSide(color: gColor.withValues(alpha: 0.5)),
      ),
      child: InkWell(
        borderRadius: BorderRadius.circular(12),
        onTap: () => _abrirDetalle(alerta),
        child: Padding(
          padding: const EdgeInsets.all(14.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Icon(Icons.report_problem_rounded, color: gColor, size: 20),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      alerta.tipoLegible.toUpperCase(),
                      style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 13),
                    ),
                  ),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                    decoration: BoxDecoration(
                      color: gColor.withValues(alpha: 0.2),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Text(alerta.gravedad, style: TextStyle(color: gColor, fontSize: 10, fontWeight: FontWeight.bold)),
                  ),
                ],
              ),
              const SizedBox(height: 6),
              Text(
                alerta.descripcion,
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
                style: const TextStyle(color: Colors.white70, fontSize: 12),
              ),
              const SizedBox(height: 8),
              Row(
                children: [
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                    decoration: BoxDecoration(
                      color: eColor.withValues(alpha: 0.18),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Text(alerta.estado.replaceAll('_', ' '),
                        style: TextStyle(color: eColor, fontSize: 10, fontWeight: FontWeight.bold)),
                  ),
                  const Spacer(),
                  Text(_formatearFecha(alerta.fechadeteccion),
                      style: const TextStyle(color: Colors.white54, fontSize: 11)),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  void _abrirDetalle(AlertModel alerta) {
    showModalBottomSheet(
      context: context,
      backgroundColor: const Color(0xFF1E293B),
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(18)),
      ),
      builder: (ctx) {
        return Padding(
          padding: const EdgeInsets.all(18.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(alerta.tipoLegible.toUpperCase(),
                  style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 16)),
              const SizedBox(height: 8),
              Text(alerta.descripcion, style: const TextStyle(color: Colors.white70, fontSize: 13)),
              const SizedBox(height: 12),
              if (alerta.numeroserie != null)
                _detalleRow('Nº de serie', alerta.numeroserie!),
              _detalleRow('Gravedad', alerta.gravedad),
              _detalleRow('Estado', alerta.estado.replaceAll('_', ' ')),
              _detalleRow('Detectada', _formatearFecha(alerta.fechadeteccion)),
              if (alerta.fecharesolucion != null)
                _detalleRow('Resuelta', _formatearFecha(alerta.fecharesolucion)),
              if (alerta.usuarioresolutorNombre != null)
                _detalleRow('Resolvió', alerta.usuarioresolutorNombre!),
              const Divider(color: Color(0xFF334155), height: 24),
              const Text('Clasificación y resolución', style: TextStyle(color: Color(0xFF94A3B8), fontSize: 12)),
              const SizedBox(height: 10),
              Row(
                children: [
                  _estadoBoton(ctx, alerta, 'pendiente', 'Pendiente', const Color(0xFFEF4444)),
                  const SizedBox(width: 8),
                  _estadoBoton(ctx, alerta, 'en_proceso', 'En proceso', const Color(0xFFF59E0B)),
                  const SizedBox(width: 8),
                  _estadoBoton(ctx, alerta, 'resuelta', 'Resuelta', const Color(0xFF10B981)),
                ],
              ),
              const SizedBox(height: 8),
            ],
          ),
        );
      },
    );
  }

  Widget _estadoBoton(BuildContext ctx, AlertModel alerta, String estado, String label, Color color) {
    final activo = alerta.estado == estado;
    return Expanded(
      child: ElevatedButton(
        style: ElevatedButton.styleFrom(
          backgroundColor: activo ? color : const Color(0xFF0F172A),
          side: BorderSide(color: color.withValues(alpha: 0.6)),
          padding: const EdgeInsets.symmetric(vertical: 10),
        ),
        onPressed: activo
            ? null
            : () async {
                final ok = await widget.controller.changeEstado(alerta.idalerta, estado);
                if (ctx.mounted) Navigator.of(ctx).pop();
                if (mounted && !ok) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(content: Text(widget.controller.errorMessage ?? 'No se pudo actualizar la alerta.')),
                  );
                }
              },
        child: Text(label, style: TextStyle(color: activo ? Colors.white : color, fontSize: 12)),
      ),
    );
  }

  Widget _detalleRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 3),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(width: 110, child: Text(label, style: const TextStyle(color: Color(0xFF94A3B8), fontSize: 12))),
          Expanded(child: Text(value, style: const TextStyle(color: Colors.white, fontSize: 13))),
        ],
      ),
    );
  }
}
