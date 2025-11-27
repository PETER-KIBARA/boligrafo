import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../api/api_service.dart';

class AuthProvider extends ChangeNotifier {
  String? _token;
  String? _patientName;
  bool _isLoading = false;
  bool _isLoggedIn = false;

  // Getters
  String? get token => _token;
  String? get patientName => _patientName;
  bool get isLoading => _isLoading;
  bool get isLoggedIn => _isLoggedIn;

  // Initialize auth state from SharedPreferences
  Future<void> initializeAuth() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final token = prefs.getString('patientToken');
      final expiryString = prefs.getString('tokenExpiry');
      final name = prefs.getString('patientName');

      if (token != null && expiryString != null) {
        final expiryDate = DateTime.tryParse(expiryString);
        if (expiryDate != null && DateTime.now().isBefore(expiryDate)) {
          _token = token;
          _patientName = name;
          _isLoggedIn = true;
        } else {
          // Token expired → clear stored data
          await _clearStoredData();
        }
      }
      notifyListeners();
    } catch (e) {
      debugPrint('Error initializing auth: $e');
    }
  }

  // Login method
  Future<Map<String, dynamic>> login({
    required String email,
    required String password,
  }) async {
    _setLoading(true);

    try {
      final response = await ApiService.login(
        email: email.trim(),
        password: password.trim(),
      );

      if (response["error"] == true) {
        _setLoading(false);
        return response;
      } else {
        // Save authentication data
        await _saveAuthData(response);
        _setLoading(false);
        return response;
      }
    } catch (e) {
      _setLoading(false);
      return {"error": true, "message": "Something went wrong: $e"};
    }
  }

  // Logout method
  Future<void> logout() async {
    await _clearStoredData();
    _isLoggedIn = false;
    notifyListeners();
  }

  // Private helper methods
  void _setLoading(bool loading) {
    _isLoading = loading;
    notifyListeners();
  }

  Future<void> _saveAuthData(Map<String, dynamic> response) async {
    final prefs = await SharedPreferences.getInstance();
    
    _token = response["token"];
    _patientName = response["name"] ?? "Patient";
    
    await prefs.setString("patientToken", _token!);
    await prefs.setString("patientName", _patientName!);
    
    // Save token expiry
    final expiryDate = DateTime.now().add(const Duration(days: 10));
    await prefs.setString("tokenExpiry", expiryDate.toIso8601String());
    
    _isLoggedIn = true;
    notifyListeners();
  }

  Future<void> _clearStoredData() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('patientToken');
    await prefs.remove('tokenExpiry');
    await prefs.remove('patientName');
    
    _token = null;
    _patientName = null;
    _isLoggedIn = false;
  }

  // Check if token is valid
  bool get isTokenValid {
    if (_token == null) return false;
    // Additional token validation logic can be added here
    return true;
  }
}
