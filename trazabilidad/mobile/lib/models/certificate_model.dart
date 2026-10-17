class CertificateEvento {
  final int idevento;
  final String tipoevento;
  final String? fechahora;
  final String? descripcion;
  final String? payloadhash;
  final bool enBlockchain;
  final bool verificado;

  CertificateEvento({
    required this.idevento,
    required this.tipoevento,
    this.fechahora,
    this.descripcion,
    this.payloadhash,
    required this.enBlockchain,
    required this.verificado,
  });

  factory CertificateEvento.fromJson(Map<String, dynamic> json) {
    return CertificateEvento(
      idevento: json['idevento'] ?? 0,
      tipoevento: json['tipoevento'] ?? '',
      fechahora: json['fechahora'],
      descripcion: json['descripcion'],
      payloadhash: json['payloadhash'],
      enBlockchain: json['en_blockchain'] ?? false,
      verificado: json['verificado'] ?? false,
    );
  }
}

class CertificateDocumento {
  final int iddocumento;
  final String nombre;
  final String tipodocumento;
  final String urlarchivo;
  final String hasharchivo;
  final String? fechaemision;
  final String? fechavencimiento;

  CertificateDocumento({
    required this.iddocumento,
    required this.nombre,
    required this.tipodocumento,
    required this.urlarchivo,
    required this.hasharchivo,
    this.fechaemision,
    this.fechavencimiento,
  });

  factory CertificateDocumento.fromJson(Map<String, dynamic> json) {
    return CertificateDocumento(
      iddocumento: json['iddocumento'] ?? 0,
      nombre: json['nombre'] ?? '',
      tipodocumento: json['tipodocumento'] ?? '',
      urlarchivo: json['urlarchivo'] ?? '',
      hasharchivo: json['hasharchivo'] ?? '',
      fechaemision: json['fechaemision'],
      fechavencimiento: json['fechavencimiento'],
    );
  }
}

class CertificateCertificacion {
  final int idcertificacion;
  final String nombre;
  final String? entidademisora;
  final String? fechaobtencion;

  CertificateCertificacion({
    required this.idcertificacion,
    required this.nombre,
    this.entidademisora,
    this.fechaobtencion,
  });

  factory CertificateCertificacion.fromJson(Map<String, dynamic> json) {
    return CertificateCertificacion(
      idcertificacion: json['idcertificacion'] ?? 0,
      nombre: json['nombre'] ?? '',
      entidademisora: json['entidademisora'],
      fechaobtencion: json['fechaobtencion'],
    );
  }
}

class UnitCertificateModel {
  final int idunidad;
  final String numeroserie;
  final String uuidpublico;
  final String? producto;
  final String? modelo;
  final String? sku;
  final String? color;
  final String? capacidad;
  final String autenticidad;
  final int totalEventos;
  final int registrosBlockchain;
  final int registrosConfirmados;
  final List<CertificateEvento> eventos;
  final List<CertificateDocumento> documentos;
  final List<CertificateCertificacion> certificaciones;

  UnitCertificateModel({
    required this.idunidad,
    required this.numeroserie,
    required this.uuidpublico,
    this.producto,
    this.modelo,
    this.sku,
    this.color,
    this.capacidad,
    required this.autenticidad,
    required this.totalEventos,
    required this.registrosBlockchain,
    required this.registrosConfirmados,
    required this.eventos,
    required this.documentos,
    required this.certificaciones,
  });

  bool get verificado => autenticidad == 'verificado';
  bool get sinDatos => autenticidad == 'sin_datos';

  factory UnitCertificateModel.fromJson(Map<String, dynamic> json) {
    return UnitCertificateModel(
      idunidad: json['idunidad'] ?? 0,
      numeroserie: json['numeroserie'] ?? '',
      uuidpublico: json['uuidpublico'] ?? '',
      producto: json['producto'],
      modelo: json['modelo'],
      sku: json['sku'],
      color: json['color'],
      capacidad: json['capacidad'],
      autenticidad: json['autenticidad'] ?? 'sin_datos',
      totalEventos: json['total_eventos'] ?? 0,
      registrosBlockchain: json['registros_blockchain'] ?? 0,
      registrosConfirmados: json['registros_confirmados'] ?? 0,
      eventos: (json['eventos'] as List<dynamic>?)
              ?.map((e) => CertificateEvento.fromJson(e))
              .toList() ??
          [],
      documentos: (json['documentos'] as List<dynamic>?)
              ?.map((e) => CertificateDocumento.fromJson(e))
              .toList() ??
          [],
      certificaciones: (json['certificaciones'] as List<dynamic>?)
              ?.map((e) => CertificateCertificacion.fromJson(e))
              .toList() ??
          [],
    );
  }
}
