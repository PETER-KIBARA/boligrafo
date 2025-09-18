import 'dart:convert';
import 'package:google_generative_ai/google_generative_ai.dart';
import 'package:shared_preferences/shared_preferences.dart';

const String _envApiKey = String.fromEnvironment('api_key');

class AiService {
  static const String _prefsKey = 'aiLifestyleTips';

  static Future<void> generateAndSaveTips({String? apiKey, required String patientName}) async {
    final String key = apiKey ?? _envApiKey;
    if (key.isEmpty) {
      return;
    }
    final model = GenerativeModel(model: 'gemini-1.5-flash', apiKey: key);
    final prompt = 'Provide 5 concise, patient-friendly lifestyle tips for hypertension management tailored for $patientName. '
        'Include diet, exercise, stress, sleep, and medication adherence. Return JSON with array tips: [{"title":"...","body":"..."}]';
    final content = [Content.text(prompt)];
    final response = await model.generateContent(content);
    final text = response.text ?? '';
    // Try parse JSON; if plain text, wrap into basic JSON.
    List tips;
    try {
      final decoded = jsonDecode(text);
      tips = decoded['tips'] as List;
    } catch (_) {
      tips = text
          .split(RegExp(r'\n+'))
          .where((e) => e.trim().isNotEmpty)
          .take(5)
          .map((e) => {'title': 'Tip', 'body': e.trim()})
          .toList();
    }
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_prefsKey, jsonEncode({'tips': tips}));
  }

  static Future<List<Map<String, dynamic>>> loadSavedTips() async {
    final prefs = await SharedPreferences.getInstance();
    final raw = prefs.getString(_prefsKey);
    if (raw == null) return [];
    final json = jsonDecode(raw) as Map<String, dynamic>;
    final List list = json['tips'] as List? ?? [];
    return list.cast<Map<String, dynamic>>();
  }
}


