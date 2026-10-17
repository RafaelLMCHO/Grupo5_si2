import 'dart:convert';
import 'package:http/http.dart' as http;
import '../core/api_config.dart';
import '../models/trace_history_model.dart';

class TraceService {
  /// Extrae el uuidpublico de un valor escaneado o escrito manualmente.
  ///
  /// Acepta tanto la URL completa del QR (https://.../trace/{uuid}) como el
  /// uuid suelto. Devuelve null si no se puede reconocer.
  static String? extractUuid(String input) {
    final raw = input.trim();
    if (raw.isEmpty) return null;

    const marker = '/trace/';
    final idx = raw.indexOf(marker);
    final candidate = idx >= 0 ? raw.substring(idx + marker.length) : raw;

    // Quita query string / fragmento y barras finales.
    var uuid = candidate.split('?').first.split('#').first;
    while (uuid.endsWith('/')) {
      uuid = uuid.substring(0, uuid.length - 1);
    }
    if (uuid.isEmpty) return null;
    return uuid;
  }

  /// CU-022: consulta pública del historial de trazabilidad (sin autenticación).
  static Future<TraceHistoryModel> fetchTrace(String uuidpublico) async {
    final uri = Uri.parse(ApiConfig.traceByUuid(uuidpublico));
    final response = await http.get(
      uri,
      headers: {'Content-Type': 'application/json'},
    );

    if (response.statusCode == 200) {
      final Map<String, dynamic> data =
          jsonDecode(utf8.decode(response.bodyBytes));
      return TraceHistoryModel.fromJson(data);
    } else if (response.statusCode == 404) {
      throw Exception('Unidad no encontrada o sin código QR activo.');
    } else {
      throw Exception('Error al consultar la trazabilidad: ${response.statusCode}');
    }
  }
}
