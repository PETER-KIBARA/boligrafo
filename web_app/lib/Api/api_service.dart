import 'dart:convert';
import 'package:http/http.dart' as http;  

class ApiService {
  static const String baseUrl = "http://192.168.100.93:8000";

  Future<Map<String, dynamic>> signup({
    required String name,
    required String email,
    required String password,
    required String confirmPassword,
    String? phone,
    String? address,
    String? dob,
    String? gender,
    String? emergencyName,
    String? emergencyPhone,
    String? emergencyRelation,
  }) async {
    final url = Uri.parse("$baseUrl/apisignup");

    final body = {
      "name": name,
      "email": email,
      "password": password,
      "confirm_password": confirmPassword,
      "phone": phone ?? "",
      "address": address ?? "",
      "dob": dob ?? "",
      "gender": gender ?? "",
      "emergency_name": emergencyName ?? "",
      "emergency_phone": emergencyPhone ?? "",
      "emergency_relation": emergencyRelation ?? "",
    };

    try {
      final response = await http.post(
        url,
        headers: {"Content-Type": "application/json"},
        body: jsonEncode(body),
      );

      if (response.statusCode == 201) {
        // ✅ Success
        return jsonDecode(response.body);
      } else {
        
        return {
          "error": true,
          "message": jsonDecode(response.body)["error"] ??
              "Something went wrong"
        };
      }
    } catch (e) {
      print(e);
      return {"error": true, "message": e.toString()};
    }
  }
}