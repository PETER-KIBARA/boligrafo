import 'dart:convert';
import 'package:http/http.dart' as http;


class ApiService {
  static const String baseUrl = "http://192.168.100.93:8000";

  
  static Future<Map<String, dynamic>> login({
    required String email,
    required String password,
  }) async {
    final url = Uri.parse("$baseUrl/apisignup");
    try {
      final response = await http.post(
        url,
        headers: {
          "Content-Type": "application/json",
        },
        body: jsonEncode({
          "email": email,
          "password": password,
        }),
      );

      if (response.statusCode == 200) {
        return jsonDecode(response.body); 
      } else {
        return {
          "error": true,
          "message": "Login failed: ${response.body}"
        };
      }
    } catch (e) {
      return {
        "error": true,
        "message": "Something went wrong: $e"
      };
    }
  }
}
