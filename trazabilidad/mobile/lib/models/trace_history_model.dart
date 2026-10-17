class TraceActorInfo {
  final String nombre;
  final String? tipo;

  TraceActorInfo({required this.nombre, this.tipo});

  factory TraceActorInfo.fromJson(Map<String, dynamic> json) {
    return TraceActorInfo(
      nombre: json['nombre'] ?? '',
      tipo: json['tipo'],
    );
  }
}

class TraceUbicacionInfo {
  final String nombre;
  final String? ciudad;
  final String? pais;

  TraceUbicacionInfo({required this.nombre, this.ciudad, this.pais});

  factory TraceUbicacionInfo.fromJson(Map<String, dynamic> json) {
    return TraceUbicacionInfo(
      nombre: json['nombre'] ?? '',
      ciudad: json['ciudad'],
      pais: json['pais'],
    );
  }

  String get ubicacionCompleta {
    final partes = [nombre, ciudad, pais].where((p) => p != null && p.isNotEmpty).toList();
    return partes.join(', ');
  }
}

class TraceProductoInfo {
  final String nombre;
  final String? paisorigen;
  final String? imagenurl;

  TraceProductoInfo({required this.nombre, this.paisorigen, this.imagenurl});

  factory TraceProductoInfo.fromJson(Map<String, dynamic> json) {
    return TraceProductoInfo(
      nombre: json['nombre'] ?? '',
      paisorigen: json['paisorigen'],
      imagenurl: json['imagenurl'],
    );
  }
}

class TraceVarianteInfo {
  final String? sku;
  final String? color;
  final String? capacidad;

  TraceVarianteInfo({this.sku, this.color, this.capacidad});

  factory TraceVarianteInfo.fromJson(Map<String, dynamic> json) {
    return TraceVarianteInfo(
      sku: json['sku'],
      color: json['color'],
      capacidad: json['capacidad'],
    );
  }

  String get descripcion {
    final partes = [color, capacidad].where((p) => p != null && p.isNotEmpty).toList();
    return partes.join(' ');
  }
}

class TraceEventoInfo {
  final String fechahora;
  final String tipoevento;
  final String? descripcion;
  final String? estadoverificacion;
  final TraceUbicacionInfo? ubicacion;
  final TraceActorInfo? actorOrigen;
  final TraceActorInfo? actorDestino;

  TraceEventoInfo({
    required this.fechahora,
    required this.tipoevento,
    this.descripcion,
    this.estadoverificacion,
    this.ubicacion,
    this.actorOrigen,
    this.actorDestino,
  });

  bool get verificado => estadoverificacion == 'verificado';

  factory TraceEventoInfo.fromJson(Map<String, dynamic> json) {
    return TraceEventoInfo(
      fechahora: json['fechahora'] ?? '',
      tipoevento: json['tipoevento'] ?? '',
      descripcion: json['descripcion'],
      estadoverificacion: json['estadoverificacion'],
      ubicacion: json['ubicacion'] != null
          ? TraceUbicacionInfo.fromJson(json['ubicacion'])
          : null,
      actorOrigen: json['actor_origen'] != null
          ? TraceActorInfo.fromJson(json['actor_origen'])
          : null,
      actorDestino: json['actor_destino'] != null
          ? TraceActorInfo.fromJson(json['actor_destino'])
          : null,
    );
  }
}

class TraceHistoryModel {
  final String uuidpublico;
  final String numeroserie;
  final String? estado;
  final String? fechaingreso;
  final String? empresa;
  final TraceProductoInfo? producto;
  final TraceVarianteInfo? variante;
  final TraceActorInfo? custodioActual;
  final TraceUbicacionInfo? ubicacionActual;
  final String? qrFechageneracion;
  final List<TraceEventoInfo> eventos;

  TraceHistoryModel({
    required this.uuidpublico,
    required this.numeroserie,
    this.estado,
    this.fechaingreso,
    this.empresa,
    this.producto,
    this.variante,
    this.custodioActual,
    this.ubicacionActual,
    this.qrFechageneracion,
    required this.eventos,
  });

  int get totalEventos => eventos.length;

  int get eventosVerificados => eventos.where((e) => e.verificado).length;

  /// CU-022: la unidad se considera auténtica/verificada si tiene historial y
  /// ningún evento fue marcado como fallido.
  bool get esAutentico {
    if (eventos.isEmpty) return false;
    return !eventos.any((e) => e.estadoverificacion == 'fallido');
  }

  factory TraceHistoryModel.fromJson(Map<String, dynamic> json) {
    return TraceHistoryModel(
      uuidpublico: json['uuidpublico'] ?? '',
      numeroserie: json['numeroserie'] ?? '',
      estado: json['estado'],
      fechaingreso: json['fechaingreso'],
      empresa: json['empresa'],
      producto: json['producto'] != null
          ? TraceProductoInfo.fromJson(json['producto'])
          : null,
      variante: json['variante'] != null
          ? TraceVarianteInfo.fromJson(json['variante'])
          : null,
      custodioActual: json['custodio_actual'] != null
          ? TraceActorInfo.fromJson(json['custodio_actual'])
          : null,
      ubicacionActual: json['ubicacion_actual'] != null
          ? TraceUbicacionInfo.fromJson(json['ubicacion_actual'])
          : null,
      qrFechageneracion: json['qr_fechageneracion'],
      eventos: (json['eventos'] as List<dynamic>?)
              ?.map((e) => TraceEventoInfo.fromJson(e))
              .toList() ??
          [],
    );
  }
}
