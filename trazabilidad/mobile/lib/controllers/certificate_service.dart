import 'dart:convert';
import 'package:http/http.dart' as http;
import '../core/api_config.dart';
import '../models/certificate_model.dart';

class CertificateService {
  /// CU-034: consulta pública (lectura) de los registros Blockchain y
  /// certificados de una unidad a partir de su UUID público (sin autenticación).
  static Future<UnitCertificateModel> fetchPublicCertificate(String uuidpublico) async {
    final uri = Uri.parse(ApiConfig.certificateByUuid(uuidpublico));
    final response = await http.get(
      uri,
      headers: {'Content-Type': 'application/json'},
    );

    if (response.statusCode == 200) {
      final Map<String, dynamic> data = jsonDecode(utf8.decode(response.bodyBytes));
      return UnitCertificateModel.fromJson(data);
    } else if (response.statusCode == 404) {
      throw Exception('No se encontró un certificado para esta unidad.');
    } else {
      throw Exception('Error al consultar el certificado: ${response.statusCode}');
    }
  }
}
