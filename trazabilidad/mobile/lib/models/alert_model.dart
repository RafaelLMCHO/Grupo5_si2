class AlertModel {
  final int idalerta;
  final int idtenant;
  final int? idunidad;
  final int? idevento;
  final String tipoalerta;
  final String descripcion;
  final String gravedad;
  final String fechadeteccion;
  final String? fecharesolucion;
  final String estado;
  final int? idusuarioresolutor;
  final String? numeroserie;
  final String? uuidpublico;
  final String? usuarioresolutorNombre;

  AlertModel({
    required this.idalerta,
    required this.idtenant,
    this.idunidad,
    this.idevento,
    required this.tipoalerta,
    required this.descripcion,
    required this.gravedad,
    required this.fechadeteccion,
    this.fecharesolucion,
    required this.estado,
    this.idusuarioresolutor,
    this.numeroserie,
    this.uuidpublico,
    this.usuarioresolutorNombre,
  });

  bool get estaResuelta => estado == 'resuelta';
  bool get esCritica => gravedad == 'critica';
  bool get estaPendiente => estado == 'pendiente';

  String get tipoLegible => tipoalerta.replaceAll('_', ' ');

  factory AlertModel.fromJson(Map<String, dynamic> json) {
    return AlertModel(
      idalerta: json['idalerta'] ?? 0,
      idtenant: json['idtenant'] ?? 0,
      idunidad: json['idunidad'],
      idevento: json['idevento'],
      tipoalerta: json['tipoalerta'] ?? '',
      descripcion: json['descripcion'] ?? '',
      gravedad: json['gravedad'] ?? 'media',
      fechadeteccion: json['fechadeteccion'] ?? '',
      fecharesolucion: json['fecharesolucion'],
      estado: json['estado'] ?? 'pendiente',
      idusuarioresolutor: json['idusuarioresolutor'],
      numeroserie: json['numeroserie'],
      uuidpublico: json['uuidpublico'],
      usuarioresolutorNombre: json['usuarioresolutor_nombre'],
    );
  }
}

class AlertListResponse {
  final int total;
  final List<AlertModel> items;

  AlertListResponse({required this.total, required this.items});

  factory AlertListResponse.fromJson(Map<String, dynamic> json) {
    final List raw = json['items'] ?? [];
    return AlertListResponse(
      total: json['total'] ?? 0,
      items: raw.map((e) => AlertModel.fromJson(e)).toList(),
    );
  }
}

class AlertSummary {
  final int total;
  final int pendientes;
  final int enProceso;
  final int resueltas;
  final int criticas;
  final Map<String, int> porGravedad;
  final Map<String, int> porTipo;

  AlertSummary({
    required this.total,
    required this.pendientes,
    required this.enProceso,
    required this.resueltas,
    required this.criticas,
    required this.porGravedad,
    required this.porTipo,
  });

  static Map<String, int> _toMap(dynamic value) {
    if (value is Map) {
      return value.map((k, v) => MapEntry(k.toString(), (v as num).toInt()));
    }
    return {};
  }

  factory AlertSummary.fromJson(Map<String, dynamic> json) {
    return AlertSummary(
      total: json['total'] ?? 0,
      pendientes: json['pendientes'] ?? 0,
      enProceso: json['en_proceso'] ?? 0,
      resueltas: json['resueltas'] ?? 0,
      criticas: json['criticas'] ?? 0,
      porGravedad: _toMap(json['por_gravedad']),
      porTipo: _toMap(json['por_tipo']),
    );
  }
}
