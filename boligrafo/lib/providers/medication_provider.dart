import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../api/api_service.dart';
import '../medication_service.dart';

class MedicationProvider extends ChangeNotifier {
  List<MedicationScheduleItem> _medications = [];
  bool _isLoading = false;
  String? _error;


  // Getters
  List<MedicationScheduleItem> get medications => _medications;
  bool get isLoading => _isLoading;
  String? get error => _error;

  List<MedicationScheduleItem> get todaysMedications => List.from(_medications);

  int get takenMedicationsCount =>
      _medications.where((med) => med.takenToday).length;

  int get pendingMedicationsCount =>
      _medications.where((med) => !med.takenToday).length;

  // Load medications from API
  Future<void> loadMedications() async {
    _setLoading(true);
    _error = null;

    try {
      final prefs = await SharedPreferences.getInstance();
      final token = prefs.getString("patientToken") ?? "";

      final List<dynamic> medicationsJson =
          await ApiService.fetchPrescriptions(token);


      _medications = medicationsJson.cast<MedicationScheduleItem>();

    } catch (e, stack) {
      _error = e.toString();
      debugPrint('Error loading medications: $e\n$stack');
      _medications = [];
    } finally {
      _setLoading(false);
    }
  }

  // Mark medication as taken
  Future<void> markMedicationTaken(int medicationId, bool taken) async {
    _setLoading(true);
    _error = null;

    try {
      final prefs = await SharedPreferences.getInstance();
      final token = prefs.getString("patientToken") ?? "";

      await ApiService.updatePrescription(
        token: token,
        prescriptionId: medicationId,
        updatedData: {"taken_today": taken},
      );

      _medications = _medications.map((med) {
        if (med.id == medicationId) {
          return med.copyWith(takenToday: taken);
        }
        return med;
      }).toList();
    } catch (e, stack) {
      _error = e.toString();
      debugPrint('Error updating medication: $e\n$stack');
    } finally {
      _setLoading(false);
    }
  }

  // Clear medications
  void clearMedications() {
    _medications.clear();
    _error = null;
    notifyListeners();
  }

  // Private helpers
  void _setLoading(bool loading) {
    _isLoading = loading;
    notifyListeners();
  }
}
