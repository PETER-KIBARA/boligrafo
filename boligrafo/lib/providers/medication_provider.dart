import 'package:flutter/material.dart';
import '../medication_service.dart';

class MedicationProvider extends ChangeNotifier {
  List<MedicationScheduleItem> _medications = [];
  bool _isLoading = false;
  String? _error;

  // Getters
  List<MedicationScheduleItem> get medications => _medications;
  bool get isLoading => _isLoading;
  String? get error => _error;

  // Load medication schedule
  Future<void> loadMedications() async {
    _setLoading(true);
    _error = null;

    try {
      final medications = await MedicationService.getSchedule();
      _medications = medications;
      _setLoading(false);
    } catch (e) {
      _error = e.toString();
      _setLoading(false);
      debugPrint('Error loading medications: $e');
    }
  }

  // Save medication schedule
  Future<void> saveMedications(List<MedicationScheduleItem> medications) async {
    _setLoading(true);
    _error = null;

    try {
      await MedicationService.saveSchedule(medications);
      _medications = medications;
      _setLoading(false);
    } catch (e) {
      _error = e.toString();
      _setLoading(false);
      debugPrint('Error saving medications: $e');
    }
  }

  // Add new medication
  Future<void> addMedication(MedicationScheduleItem medication) async {
    final updatedMedications = List<MedicationScheduleItem>.from(_medications)
      ..add(medication);
    await saveMedications(updatedMedications);
  }

  // Update medication
  Future<void> updateMedication(MedicationScheduleItem medication) async {
    final updatedMedications = _medications.map((med) {
      if (med.id == medication.id) {
        return medication;
      }
      return med;
    }).toList();
    await saveMedications(updatedMedications);
  }

  // Remove medication
  Future<void> removeMedication(String medicationId) async {
    final updatedMedications = _medications
        .where((med) => med.id != medicationId)
        .toList();
    await saveMedications(updatedMedications);
  }

  // Mark medication as taken today
  Future<void> markMedicationTaken(String medicationId, bool taken) async {
    final updatedMedications = _medications.map((med) {
      if (med.id == medicationId) {
        return med.copyWith(takenToday: taken);
      }
      return med;
    }).toList();
    await saveMedications(updatedMedications);
  }

  // Clear medications
  void clearMedications() {
    _medications = [];
    _error = null;
    notifyListeners();
  }

  // Private helper method
  void _setLoading(bool loading) {
    _isLoading = loading;
    notifyListeners();
  }

  // Get medications for today
  List<MedicationScheduleItem> get todaysMedications {
    return _medications.where((med) {
      // You can add logic here to filter by current time
      // For now, returning all medications
      return true;
    }).toList();
  }

  // Get taken medications count for today
  int get takenMedicationsCount {
    return _medications.where((med) => med.takenToday).length;
  }

  // Get pending medications count for today
  int get pendingMedicationsCount {
    return _medications.where((med) => !med.takenToday).length;
  }
}
