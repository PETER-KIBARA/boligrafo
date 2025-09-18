import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

class ApiService {
  static const String baseUrl = "http://192.168.100.93:8000";

  // ---------- LOGIN ----------
static Future<Map<String, dynamic>> login({
  required String email,
  required String password,
}) async {
  final url = Uri.parse("$baseUrl/apilogin");
  try {
    final response = await http.post(
      url,
      headers: {"Content-Type": "application/json"},
      body: jsonEncode({"email": email, "password": password}),
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);

      final prefs = await SharedPreferences.getInstance();
      await prefs.setString("patientToken", data["token"]);

      // 👇 Save the patient’s name from response["user"]["name"]
      if (data["user"] != null) {
        await prefs.setString("patientName", data["user"]["name"] ?? "Patient");
      }

      return data;
    } else {
      return {"error": true, "message": "Login failed: ${response.body}"};
    }
  } catch (e) {
    return {"error": true, "message": "Something went wrong: $e"};
  }
}



  // ---------- SAVE VITAL (CREATE) ----------
 static Future<Map<String, dynamic>> saveVital({
  required String token,
  required int systolic,
  required int diastolic,
  int? heartRate,
  String? symptoms,
  String? diet,
  String? exercise,
}) async {
    final url = Uri.parse("$baseUrl/vitals");
    try {
      final response = await http.post(
        url,
        headers: {
          "Content-Type": "application/json",
          "Authorization": "Token $token",
        },
        body: jsonEncode({
          "systolic": systolic,
          "diastolic": diastolic,
          "heartrate": heartRate,
          "symptoms": symptoms ?? "",
          "diet": diet ?? "",
          "exercise": exercise ?? "",
        }),
      );

      if (response.statusCode == 201) {
        return jsonDecode(response.body); // created vital
      } else {
        return {"error": true, "message": "Save failed: ${response.body}"};
      }
    } catch (e) {
      return {"error": true, "message": "Something went wrong: $e"};
    }
  }

  // ---------- LIST VITALS (READ) ----------
  static Future<List<dynamic>> fetchVitals(String token) async {
    final url = Uri.parse("$baseUrl/vitals");
    final response = await http.get(url, headers: {"Authorization": "Token $token"});

    if (response.statusCode == 200) {
      return jsonDecode(response.body) as List;
    } else {
      throw Exception("Failed to load vitals: ${response.body}");
    }
  }
}
