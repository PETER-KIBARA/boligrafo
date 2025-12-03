import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../api/api_service.dart';
import '../models/medication_service.dart';

class MedicationProvider extends ChangeNotifier {
  late final MedicationService _medService;

  MedicationProvider({required String apiBaseUrl, required String token}) {
    _medService = MedicationService(apiBaseUrl: apiBaseUrl, token: token);
  }
  List<MedicationScheduleItem> _medications = [];
  bool _isLoading = false;
  String? _error;

  // -------------------- Getters --------------------
  List<MedicationScheduleItem> get medications => _medications;
  bool get isLoading => _isLoading;
  String? get error => _error;

  int get totalTaken =>
      _medications.fold(0, (sum, med) => sum + med.doses.where((d) => d.isTaken).length);

  int get totalPending =>
      _medications.fold(0, (sum, med) => sum + med.doses.where((d) => !d.isTaken).length);

  // -------------------- Load Medications --------------------
  Future<void> loadMedications() async {
    _setLoading(true);
    _error = null;

    try {
      final prefs = await SharedPreferences.getInstance();
      final token = prefs.getString("patientToken") ?? "";

      final List<MedicationScheduleItem> fetched =
          await ApiService.fetchPrescriptions(token);

      _medications = fetched;
      notifyListeners();
    } catch (e, stack) {
      _error = e.toString();
      debugPrint('Error loading medications: $e\n$stack');
      _medications = [];
      notifyListeners();
    } finally {
      _setLoading(false);
    }
  }

  // -------------------- Log a single dose --------------------
Future<void> logDoseTaken(int prescriptionId, String doseKey) async {
  _setLoading(true);
  _error = null;

  try {
    // Update backend + local storage
    final success = await _medService.logDoseTaken(prescriptionId, doseKey, true);
    if (!success) throw Exception("Failed to log dose on server");

    // Update local state for UI
    _medications = _medications.map((med) {
      if (med.id == prescriptionId) {
        final updatedDoses = med.doses.map((d) {
          if (d.backendKey == doseKey) {
            return d.copyWith(isTaken: true, doseTime: DateTime.now().toIso8601String());
          }
          return d;
        }).toList();
        return med.copyWith(doses: updatedDoses);
      }
      return med;
    }).toList();

    notifyListeners();
  } catch (e, stack) {
    _error = e.toString();
    debugPrint('Error logging dose: $e\n$stack');
  } finally {
    _setLoading(false);
  }
}

  // -------------------- Mark all doses for a prescription --------------------
  Future<void> markAllDoses(int prescriptionId, bool taken) async {
    _setLoading(true);
    _error = null;

    try {
      final prefs = await SharedPreferences.getInstance();
      final token = prefs.getString("patientToken") ?? "";
      final timestamp = taken ? DateTime.now().toIso8601String() : null;

      // Update backend
      await ApiService.updatePrescription(
        token: token,
        prescriptionId: prescriptionId,
        updatedData: {
          "taken_today": taken,
        },
      );

      // Update local state
      _medications = _medications.map((med) {
        if (med.id == prescriptionId) {
          final updatedDoses = med.doses
              .map((d) => d.copyWith(isTaken: taken, doseTime: timestamp))
              .toList();
          return med.copyWith(doses: updatedDoses);
        }
        return med;
      }).toList();

      // Persist locally
      await _medService.setAllTakenToday(prescriptionId, taken);

      notifyListeners();
    } catch (e, stack) {
      _error = e.toString();
      debugPrint('Error marking all doses: $e\n$stack');
    } finally {
      _setLoading(false);
    }
  }

  // -------------------- Clear all --------------------
  void clearMedications() {
    _medications.clear();
    _error = null;
    notifyListeners();
  }

  // -------------------- Private Helpers --------------------
  void _setLoading(bool loading) {
    _isLoading = loading;
    notifyListeners();
  }
}
