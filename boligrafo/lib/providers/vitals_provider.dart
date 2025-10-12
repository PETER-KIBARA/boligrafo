import 'package:flutter/material.dart';
import '../api/api_service.dart';

class VitalsProvider extends ChangeNotifier {
  List<dynamic> _vitals = [];
  bool _isLoading = false;
  String? _error;

  // Getters
  List<dynamic> get vitals => _vitals;
  bool get isLoading => _isLoading;
  String? get error => _error;

  // Fetch vitals from API
  Future<void> fetchVitals(String token) async {
    _setLoading(true);
    _error = null;

    try {
      final vitalsData = await ApiService.fetchVitals(token);
      _vitals = vitalsData;
      _setLoading(false);
    } catch (e) {
      _error = e.toString();
      _setLoading(false);
      debugPrint('Error fetching vitals: $e');
    }
  }

  // Save new vital reading
  Future<Map<String, dynamic>> saveVital({
    required String token,
    required int systolic,
    required int diastolic,
    int? heartRate,
    String? symptoms,
    String? diet,
    String? exercise,
  }) async {
    _setLoading(true);
    _error = null;

    try {
      final response = await ApiService.saveVital(
        token: token,
        systolic: systolic,
        diastolic: diastolic,
        heartRate: heartRate,
        symptoms: symptoms,
        diet: diet,
        exercise: exercise,
      );

      if (response["error"] == true) {
        _error = response["message"];
        _setLoading(false);
        return response;
      } else {
        // Refresh vitals after successful save
        await fetchVitals(token);
        return response;
      }
    } catch (e) {
      _error = e.toString();
      _setLoading(false);
      return {"error": true, "message": "Something went wrong: $e"};
    }
  }

  // Clear vitals data
  void clearVitals() {
    _vitals = [];
    _error = null;
    notifyListeners();
  }

  // Private helper method
  void _setLoading(bool loading) {
    _isLoading = loading;
    notifyListeners();
  }

  // Get latest vital reading
  Map<String, dynamic>? get latestVital {
    if (_vitals.isEmpty) return null;
    
    // Sort by date (assuming the API returns vitals with date field)
    final sortedVitals = List<Map<String, dynamic>>.from(_vitals)
      ..sort((a, b) {
        final dateA = DateTime.tryParse(a['created_at'] ?? a['date'] ?? '');
        final dateB = DateTime.tryParse(b['created_at'] ?? b['date'] ?? '');
        
        if (dateA == null || dateB == null) return 0;
        return dateB.compareTo(dateA);
      });
    
    return sortedVitals.isNotEmpty ? sortedVitals.first : null;
  }

  // Get vitals for chart display
  List<Map<String, dynamic>> get vitalsForChart {
    if (_vitals.isEmpty) return [];
    
    final sortedVitals = List<Map<String, dynamic>>.from(_vitals)
      ..sort((a, b) {
        final dateA = DateTime.tryParse(a['created_at'] ?? a['date'] ?? '');
        final dateB = DateTime.tryParse(b['created_at'] ?? b['date'] ?? '');
        
        if (dateA == null || dateB == null) return 0;
        return dateA.compareTo(dateB);
      });
    
    return sortedVitals;
  }
}
