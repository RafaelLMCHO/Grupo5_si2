import 'package:flutter/material.dart';
import '../models/alert_model.dart';
import 'alert_service.dart';

class AlertController extends ChangeNotifier {
  List<AlertModel> alerts = [];
  AlertSummary? summary;
  bool isLoading = false;
  String? errorMessage;
  String? filtroEstado;

  Future<void> load({String? estado}) async {
    filtroEstado = estado;
    isLoading = true;
    errorMessage = null;
    notifyListeners();

    try {
      final result = await AlertService.fetchAlerts(estado: estado);
      alerts = result.items;
      summary = await AlertService.fetchSummary();
    } catch (e) {
      errorMessage = e.toString().replaceAll('Exception: ', '');
    } finally {
      isLoading = false;
      notifyListeners();
    }
  }

  Future<bool> changeEstado(int idalerta, String estado, {String? comentario}) async {
    try {
      final updated = await AlertService.updateEstado(idalerta, estado, comentario: comentario);
      final idx = alerts.indexWhere((a) => a.idalerta == idalerta);
      if (idx >= 0) alerts[idx] = updated;
      summary = await AlertService.fetchSummary();
      notifyListeners();
      return true;
    } catch (e) {
      errorMessage = e.toString().replaceAll('Exception: ', '');
      notifyListeners();
      return false;
    }
  }
}
