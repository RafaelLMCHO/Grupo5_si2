import 'dart:convert';
import 'package:http/http.dart' as http;
import '../core/api_config.dart';
import '../core/secure_storage.dart';
import '../models/alert_model.dart';

class AlertService {
  static Future<Map<String, String>> _authHeaders() async {
    final token = await SecureStorageService.getToken();
    if (token == null) {
      throw Exception('No autenticado. Inicie sesión nuevamente.');
    }
    return {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer $token',
    };
  }

  static String _errorMessage(http.Response response) {
    try {
      final data = jsonDecode(response.body);
      if (data is Map && data['detail'] != null) {
        return data['detail'].toString();
      }
    } catch (_) {}
    return 'Error del servidor (${response.statusCode})';
  }

  /// CU-024: listado de alertas e incidencias de la empresa.
  static Future<AlertListResponse> fetchAlerts({
    String? estado,
    String? tipoalerta,
    String? gravedad,
    int skip = 0,
    int limit = 100,
  }) async {
    final headers = await _authHeaders();
    final params = <String, String>{
      'skip': skip.toString(),
      'limit': limit.toString(),
    };
    if (estado != null && estado.isNotEmpty) params['estado'] = estado;
    if (tipoalerta != null && tipoalerta.isNotEmpty) params['tipoalerta'] = tipoalerta;
    if (gravedad != null && gravedad.isNotEmpty) params['gravedad'] = gravedad;

    final uri = Uri.parse(ApiConfig.alerts).replace(queryParameters: params);
    final response = await http.get(uri, headers: headers);

    if (response.statusCode == 200) {
      return AlertListResponse.fromJson(jsonDecode(utf8.decode(response.bodyBytes)));
    }
    throw Exception(_errorMessage(response));
  }

  /// CU-024: resumen de alertas por estado, gravedad y tipo.
  static Future<AlertSummary> fetchSummary() async {
    final headers = await _authHeaders();
    final response = await http.get(Uri.parse(ApiConfig.alertSummary), headers: headers);
    if (response.statusCode == 200) {
      return AlertSummary.fromJson(jsonDecode(utf8.decode(response.bodyBytes)));
    }
    throw Exception(_errorMessage(response));
  }

  /// CU-024: clasificar o resolver una alerta.
  static Future<AlertModel> updateEstado(
    int idalerta,
    String estado, {
    String? comentario,
  }) async {
    final headers = await _authHeaders();
    final response = await http.patch(
      Uri.parse(ApiConfig.alertEstado(idalerta)),
      headers: headers,
      body: jsonEncode({
        'estado': estado,
        if (comentario != null && comentario.isNotEmpty) 'comentario': comentario,
      }),
    );
    if (response.statusCode == 200) {
      return AlertModel.fromJson(jsonDecode(utf8.decode(response.bodyBytes)));
    }
    throw Exception(_errorMessage(response));
  }

  /// CU-023: reporte público de sospecha (sin autenticación).
  static Future<String> reportSuspicion({
    String? uuidpublico,
    String? numeroserie,
    required String motivo,
    String? descripcion,
    String? evidencia,
    String? nombrereportante,
    String? contactoreportante,
  }) async {
    final response = await http.post(
      Uri.parse(ApiConfig.reportSuspicion),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        if (uuidpublico != null && uuidpublico.isNotEmpty) 'uuidpublico': uuidpublico,
        if (numeroserie != null && numeroserie.isNotEmpty) 'numeroserie': numeroserie,
        'motivo': motivo,
        if (descripcion != null && descripcion.isNotEmpty) 'descripcion': descripcion,
        if (evidencia != null && evidencia.isNotEmpty) 'evidencia': evidencia,
        if (nombrereportante != null && nombrereportante.isNotEmpty)
          'nombrereportante': nombrereportante,
        if (contactoreportante != null && contactoreportante.isNotEmpty)
          'contactoreportante': contactoreportante,
      }),
    );

    if (response.statusCode == 201) {
      final data = jsonDecode(utf8.decode(response.bodyBytes));
      return (data['referencia'] ?? '').toString();
    }
    throw Exception(_errorMessage(response));
  }
}
