import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';
import 'notifications_service.dart';

class MedicationScheduleItem {
  final  int id; 
  final String name;
  final String time; 
  final bool takenToday;
  final int notificationId;

  MedicationScheduleItem({
    required this.id,
    required this.name,
    required this.time,
    required this.takenToday,
    required this.notificationId,
  });

  MedicationScheduleItem copyWith({
    int? id,
    String? name,
    String? time,
    bool? takenToday,
    int? notificationId,
  }) {
    return MedicationScheduleItem(
      id: id ?? this.id,
      name: name ?? this.name,
      time: time ?? this.time,
      takenToday: takenToday ?? this.takenToday,
      notificationId: notificationId ?? this.notificationId,
    );
  }

  Map<String, dynamic> toJson() => {
        'id': id,
        'name': name,
        'time': time,
        'takenToday': takenToday,
        'notificationId': notificationId,
      };

  static MedicationScheduleItem fromJson(Map<String, dynamic> json) =>
      MedicationScheduleItem(
        id: json['id'],
        name: json['name'],
        time: json['time'],
        takenToday: json['takenToday'] ?? false,
        notificationId: json['notificationId'] ?? 0,
      );
}

class MedicationService {
  static const String _storageKey = 'medicationSchedule';

  static Future<List<MedicationScheduleItem>> getSchedule() async {
    final prefs = await SharedPreferences.getInstance();
    final raw = prefs.getString(_storageKey);
    if (raw == null) return [];
    final List list = jsonDecode(raw) as List;
    return list
        .map((e) => MedicationScheduleItem.fromJson(e as Map<String, dynamic>))
        .toList();
  }

  static Future<void> saveSchedule(List<MedicationScheduleItem> items) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(
      _storageKey,
      jsonEncode(items.map((e) => e.toJson()).toList()),
    );
  }

  /// Parse "HH:mm" into hour/minute
  static Map<String, int> _parseTime(String hhmm) {
    final parts = hhmm.split(':');
    final hour = int.parse(parts[0]);
    final minute = int.parse(parts[1]);
    return {'hour': hour, 'minute': minute};
  }

  static Future<void> scheduleNotifications(
      List<MedicationScheduleItem> items) async {
    for (final item in items) {
      final parsed = _parseTime(item.time);
      await NotificationsService.scheduleDailyReminder(
        id: item.notificationId,
        hour: parsed['hour']!,
        minute: parsed['minute']!,
        title: 'Medication Reminder',
        body: 'Time to take ${item.name}',
      );
    }
  }

  static Future<void> setTakenToday(String id, bool taken) async {
    final items = await getSchedule();
    final updated = items
        .map((e) => e.id == id ? e.copyWith(takenToday: taken) : e)
        .toList();
    await saveSchedule(updated);
  }
}
