import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:myapp/models/medication_service.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:dio/dio.dart';
import 'package:path_provider/path_provider.dart';
import 'dart:io';

class ApiService {
  static const String baseUrl = "http://192.168.100.159:8000/api";

  //  Patient login
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

        // token expiry – adjust as needed
        final expiryDate = DateTime.now().add(const Duration(hours: 1));
        await prefs.setString("tokenExpiry", expiryDate.toIso8601String());

        if (data["user"] != null) {
          await prefs.setString(
              "patientName", data["user"]["name"] ?? "Patient");
        }

        return data;
      } else {
        return {"error": true, "message": "Login failed: ${response.body}"};
      }
    } catch (e) {
      return {"error": true, "message": "Something went wrong: $e"};
    }
  }

  //  Save BP Reading
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
          "heartrate": heartRate ?? 0,
          "symptoms": symptoms ?? "",
          "diet": diet ?? "",
          "exercise": exercise ?? "",
        }),
      );

      if (response.statusCode == 201) {
        return jsonDecode(response.body);
      } else {
        return {"error": true, "message": "Save failed: ${response.body}"};
      }
    } catch (e) {
      return {"error": true, "message": "Something went wrong: $e"};
    }
  }

  //  Fetch BP Readings
  static Future<List<dynamic>> fetchVitals(String token) async {
    final url = Uri.parse("$baseUrl/vitals");
    try {
      final response = await http.get(
        url,
        headers: {"Authorization": "Token $token"},
      );

      if (response.statusCode == 200) {
        return jsonDecode(response.body) as List;
      } else {
        throw Exception("Failed to load vitals: ${response.body}");
      }
    } catch (e) {
      throw Exception("Error fetching vitals: $e");
    }
  }

  /// Fetch all prescriptions for the logged-in patient
  static Future<List<MedicationScheduleItem>> fetchPrescriptions(String token) async {
  final url = Uri.parse("$baseUrl/patient/prescriptions"); // ✅ uses PrescriptionListCreateView
  final response = await http.get(
    url,
    headers: {
      "Content-Type": "application/json",
      "Authorization": "Token $token",
    },
  );

  if (response.statusCode == 200) {
    final List data = jsonDecode(response.body);
    return data.map((item) => MedicationScheduleItem.fromJson(item)).toList();
  } else {
    throw Exception("Failed to fetch prescriptions: ${response.body}");
  }
}


  /// Fetch a single prescription by ID
  static Future<MedicationScheduleItem> fetchPrescriptionDetail({
    required String token,
    required int prescriptionId,
  }) async {
    final url = Uri.parse("$baseUrl/patient/prescriptions/$prescriptionId");
    final response = await http.get(
      url,
      headers: {
        "Content-Type": "application/json",
        "Authorization": "Token $token",
      },
    );

    if (response.statusCode == 200) {
      return MedicationScheduleItem.fromJson(jsonDecode(response.body));
    } else {
      throw Exception("Failed to fetch prescription detail: ${response.body}");
    }
  }

  /// Update a prescription (PATCH)
  static Future<void> updatePrescription({
    required String token,
    required int prescriptionId,
    required Map<String, dynamic> updatedData,
  }) async {
    final url = Uri.parse("$baseUrl/patient/prescriptions/$prescriptionId");
    final response = await http.patch(
      url,
      headers: {
        "Content-Type": "application/json",
        "Authorization": "Token $token",
      },
      body: jsonEncode(updatedData),
    );

    if (response.statusCode != 200) {
      throw Exception("Failed to update prescription: ${response.body}");
    }
  }

/// Log a specific dose as taken
/// Log a specific dose as taken
static Future<void> logDoseTaken({
  required String token,
  required int prescriptionId,
  required String doseKey, // e.g., "morning", "afternoon", "evening"
}) async {
  final url = Uri.parse("$baseUrl/patient/prescriptions/$prescriptionId/");
  final response = await http.patch(
    url,
    headers: {
      "Content-Type": "application/json",
      "Authorization": "Token $token",
    },
    body: jsonEncode({
      "taken_today": true,       // <- backend expects this
      "dose_label": doseKey,     // <- matches backend field
    }),
  );

  if (response.statusCode != 200) {
    throw Exception("Failed to log dose: ${response.body}");
  }
}




  /// Get current user info using the token
  static Future<Map<String, dynamic>> getCurrentUser(String token) async {
    final url = Uri.parse("$baseUrl/user/me");
    try {
      final response = await http.get(
        url,
        headers: {
          "Content-Type": "application/json",
          "Authorization": "Token $token",
        },
      );

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        return {"error": true, "message": "Failed to fetch user: ${response.body}"};
      }
    } catch (e) {
      return {"error": true, "message": "Something went wrong: $e"};
    }
  }

  /// Fetch AI suggestions for a specific patient
  static Future<Map<String, dynamic>> fetchAISuggestions({
    required String token,
    required int userId,
  }) async {
    final url = Uri.parse("$baseUrl/generate_suggestions/$userId/");
    try {
      final response = await http.get(
        url,
        headers: {
          "Content-Type": "application/json",
          "Authorization": "Token $token",
        },
      );

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        return {"error": true, "message": "Failed to fetch AI suggestions: ${response.body}"};
      }
    } catch (e) {
      return {"error": true, "message": "Something went wrong fetching suggestions: $e"};
    }
  }

  /// Download and save patient report PDF
  static Future<String?> downloadReportPdf({
    required String token,
  }) async {
    final dio = Dio();
    final url = "$baseUrl/reports/pdf/";
    
    try {
      final directory = await getApplicationDocumentsDirectory();
      final filePath = "${directory.path}/medical_report_${DateTime.now().millisecondsSinceEpoch}.pdf";

      final response = await dio.download(
        url,
        filePath,
        options: Options(
          headers: {
            "Authorization": "Token $token",
          },
        ),
      );

      if (response.statusCode == 200) {
        return filePath;
      } else {
        return null;
      }
    } catch (e) {
      print("Error downloading PDF: $e");
      return null;
    }
  }
}




