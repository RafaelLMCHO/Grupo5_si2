import 'package:flutter/material.dart';
import '../models/trace_history_model.dart';
import 'trace_service.dart';

class TraceController extends ChangeNotifier {
  TraceHistoryModel? trace;
  bool isLoading = false;
  String? errorMessage;
  String? lastQuery;

  /// Carga el historial a partir de un uuid o de la URL escaneada del QR.
  Future<TraceHistoryModel?> load(String uuidOrUrl) async {
    final uuid = TraceService.extractUuid(uuidOrUrl);
    if (uuid == null) {
      errorMessage = 'Código QR no válido.';
      notifyListeners();
      return null;
    }

    lastQuery = uuid;
    isLoading = true;
    errorMessage = null;
    trace = null;
    notifyListeners();

    try {
      trace = await TraceService.fetchTrace(uuid);
      return trace;
    } catch (e) {
      errorMessage = e.toString().replaceAll('Exception: ', '');
      return null;
    } finally {
      isLoading = false;
      notifyListeners();
    }
  }

  void clear() {
    trace = null;
    errorMessage = null;
    lastQuery = null;
    isLoading = false;
    notifyListeners();
  }
}
