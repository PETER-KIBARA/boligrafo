import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:http/http.dart' as http;

/// Represents a single dose of a medication
class DoseLog {
  final String timeLabel;
  final String backendKey;
  final String? doseTime;
  final bool isTaken;

  DoseLog({
    required this.timeLabel,
    required this.backendKey,
    this.doseTime,
    this.isTaken = false,
  });

  DoseLog copyWith({String? doseTime, bool? isTaken}) {
    return DoseLog(
      timeLabel: timeLabel,
      backendKey: backendKey,
      doseTime: doseTime ?? this.doseTime,
      isTaken: isTaken ?? this.isTaken,
    );
  }

  Map<String, dynamic> toJson() => {
        'timeLabel': timeLabel,
        'backendKey': backendKey,
        'doseTime': doseTime,
        'isTaken': isTaken,
      };

  factory DoseLog.fromJson(Map<String, dynamic> json) => DoseLog(
        timeLabel: json['timeLabel'] ?? 'Daily',
        backendKey: json['backendKey'] ?? 'daily',
        doseTime: json['doseTime'],
        isTaken: json['isTaken'] ?? false,
      );
}

/// Medication with multiple doses
class MedicationScheduleItem {
  final int id;
  final String name;
  final String dosage;
  final String frequency;
  final List<DoseLog> doses;
  final int notificationId;

  MedicationScheduleItem({
    required this.id,
    required this.name,
    required this.dosage,
    required this.frequency,
    required this.doses,
    required this.notificationId,
  });

  MedicationScheduleItem copyWith({List<DoseLog>? doses}) {
    return MedicationScheduleItem(
      id: id,
      name: name,
      dosage: dosage,
      frequency: frequency,
      doses: doses ?? this.doses,
      notificationId: notificationId,
    );
  }

  Map<String, dynamic> toJson() => {
        'id': id,
        'name': name,
        'dosage': dosage,
        'frequency': frequency,
        'doses': doses.map((d) => d.toJson()).toList(),
        'notificationId': notificationId,
      };

  factory MedicationScheduleItem.fromJson(Map<String, dynamic> json) {
    final logs = (json['doses'] as List<dynamic>?)
            ?.map((e) => DoseLog.fromJson(e as Map<String, dynamic>))
            .toList() ??
        _defaultDosesFromFrequency(json['frequency'] ?? '');
    return MedicationScheduleItem(
      id: json['id'],
      name: json['name'] ?? json['medication'] ?? '',
      dosage: json['dosage'] ?? '',
      frequency: json['frequency'] ?? '',
      doses: logs,
      notificationId: json['notificationId'] ?? 0,
    );
  }

  static List<DoseLog> _defaultDosesFromFrequency(String frequency) {
    frequency = frequency.toLowerCase();
    if (frequency.contains('3') || frequency.contains('tid')) {
      return [
        DoseLog(timeLabel: 'Morning', backendKey: 'morning'),
        DoseLog(timeLabel: 'Afternoon', backendKey: 'afternoon'),
        DoseLog(timeLabel: 'Evening', backendKey: 'evening'),
      ];
    } else if (frequency.contains('2') || frequency.contains('bid')) {
      return [
        DoseLog(timeLabel: 'Morning', backendKey: 'morning'),
        DoseLog(timeLabel: 'Evening', backendKey: 'evening'),
      ];
    } else if (frequency.contains('4') || frequency.contains('qid')) {
      return [
        DoseLog(timeLabel: 'Morning', backendKey: 'morning'),
        DoseLog(timeLabel: 'Noon', backendKey: 'noon'),
        DoseLog(timeLabel: 'Evening', backendKey: 'evening'),
        DoseLog(timeLabel: 'Night', backendKey: 'night'),
      ];
    } else {
      return [
        DoseLog(timeLabel: 'Daily', backendKey: 'daily'),
      ];
    }
  }
}

/// Updated service with backend sync
class MedicationService {
  static const String _storageKey = 'medicationSchedule';
  final String apiBaseUrl;
  final String token;

  MedicationService({required this.apiBaseUrl, required this.token});

  /// Local storage getters
  Future<List<MedicationScheduleItem>> getSchedule() async {
    final prefs = await SharedPreferences.getInstance();
    final raw = prefs.getString(_storageKey);
    if (raw == null) return [];
    final list = jsonDecode(raw) as List;
    return list
        .map((e) => MedicationScheduleItem.fromJson(e as Map<String, dynamic>))
        .toList();
  }

  Future<void> saveSchedule(List<MedicationScheduleItem> items) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(
      _storageKey,
      jsonEncode(items.map((e) => e.toJson()).toList()),
    );
  }

  /// Sync a single dose with backend
  Future<bool> logDoseTaken(
      int prescriptionId, String doseKey, bool taken) async {
    final url = Uri.parse('$apiBaseUrl/prescription/$prescriptionId/');
    final response = await http.patch(
      url,
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
      body: jsonEncode({'taken_today': taken, 'dose_label': doseKey}),
    );

    if (response.statusCode == 200) {
      // Update local storage too
      final timestamp = taken ? DateTime.now().toIso8601String() : null;
      final items = await getSchedule();
      final updated = items.map((med) {
        if (med.id == prescriptionId) {
          final updatedDoses = med.doses.map((d) {
            if (d.backendKey == doseKey) {
              return d.copyWith(doseTime: timestamp, isTaken: taken);
            }
            return d;
          }).toList();
          return med.copyWith(doses: updatedDoses);
        }
        return med;
      }).toList();
      await saveSchedule(updated);
      return true;
    }
    return false;
  }

  /// Mark all doses of a medication as taken or not
  Future<void> setAllTakenToday(int prescriptionId, bool taken) async {
    final items = await getSchedule();
    final updated = items.map((med) {
      if (med.id == prescriptionId) {
        final updatedDoses = med.doses
            .map((d) => d.copyWith(
                isTaken: taken,
                doseTime: taken ? DateTime.now().toIso8601String() : null))
            .toList();
        return med.copyWith(doses: updatedDoses);
      }
      return med;
    }).toList();
    await saveSchedule(updated);

    // Optional: Sync each dose with backend
    for (var med in updated) {
      if (med.id == prescriptionId) {
        for (var dose in med.doses) {
          await logDoseTaken(prescriptionId, dose.backendKey, taken);
        }
      }
    }
  }
}
