import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'package:timezone/timezone.dart' as tz;
import 'package:timezone/data/latest.dart' as tz;
import 'dart:convert';
import 'package:flutter/material.dart';

class NotificationsService {
  static final FlutterLocalNotificationsPlugin _notificationsPlugin =
      FlutterLocalNotificationsPlugin();

  static bool _isInitialized = false;

  // Notification channels
  static const String _medicationChannelId = 'medication_reminders';
  static const String _medicationChannelName = 'Medication Reminders';
  static const String _medicationChannelDescription = 'Daily reminders to take your medication';

  static Future<void> initialize() async {
    if (_isInitialized) return;

    try {
      // Initialize timezone for scheduling
      tz.initializeTimeZones();

      // Request notification permissions (for iOS)
      final bool? granted = await _requestPermissions();
      if (granted == false) {
        print('Notification permissions not granted');
        return;
      }

      // Configure Android notification channel
      const AndroidNotificationChannel channel = AndroidNotificationChannel(
        _medicationChannelId,
        _medicationChannelName,
        description: _medicationChannelDescription,
        importance: Importance.high,
        // priority: Priority.high,
        sound: const RawResourceAndroidNotificationSound('notification_sound'),
        enableVibration: true,
        // vibrationPattern: Int64List.fromList([0, 250, 250, 250]),
        showBadge: true,
        playSound: true,
      );

      // Create notification channel
      await _notificationsPlugin
          .resolvePlatformSpecificImplementation<AndroidFlutterLocalNotificationsPlugin>()
          ?.createNotificationChannel(channel);

      // Initialize notifications plugin
      const AndroidInitializationSettings androidSettings =
          AndroidInitializationSettings('@mipmap/ic_launcher');

      // For iOS - remove the priority parameter
      const DarwinInitializationSettings iosSettings = DarwinInitializationSettings(
        requestAlertPermission: true,
        requestBadgePermission: true,
        requestSoundPermission: true,
        // defaultPresentAlert: true, // Optional
        // defaultPresentBadge: true, // Optional
        // defaultPresentSound: true, // Optional
      );

      const InitializationSettings initSettings = InitializationSettings(
        android: androidSettings,
        iOS: iosSettings,
      );

      await _notificationsPlugin.initialize(
        initSettings,
        onDidReceiveNotificationResponse: _onNotificationTap,
        onDidReceiveBackgroundNotificationResponse: _onBackgroundNotificationTap,
      );

      _isInitialized = true;
      print('NotificationsService initialized successfully');
    } catch (e) {
      print('Error initializing NotificationsService: $e');
    }
  }

  static Future<bool?> _requestPermissions() async {
    try {
      // For Android, permissions are generally granted
      // For iOS, we need to request
      final bool? result = await _notificationsPlugin
          .resolvePlatformSpecificImplementation<IOSFlutterLocalNotificationsPlugin>()
          ?.requestPermissions(
            alert: true,
            badge: true,
            sound: true,
          );
      return result;
    } catch (e) {
      print('Error requesting permissions: $e');
      return true; // Assume granted for Android
    }
  }

  /// Schedule a daily medication reminder
  static Future<int> scheduleDailyReminder({
    required int id,
    required int hour,
    required int minute,
    required String title,
    required String body,
    String? payload,
  }) async {
    try {
      await initialize(); // Ensure service is initialized

      const AndroidNotificationDetails androidDetails = AndroidNotificationDetails(
        _medicationChannelId,
        _medicationChannelName,
        channelDescription: _medicationChannelDescription,
        importance: Importance.high,
        priority: Priority.high,
        ticker: 'Medication Reminder',
        autoCancel: true,
        enableLights: true,
        color: Color(0xFF2196F3),
        ledColor: Color(0xFF2196F3),
        ledOnMs: 1000,
        ledOffMs: 500,
        sound: const RawResourceAndroidNotificationSound('notification_sound'),
        playSound: true,
        enableVibration: true,
        // vibrationPattern: Int64List.fromList([0, 250, 250, 250]),
        timeoutAfter: 3600000, // Auto-cancel after 1 hour
        styleInformation: BigTextStyleInformation(''),
      );

      // iOS notification details - removed unsupported parameters
      const DarwinNotificationDetails iosDetails = DarwinNotificationDetails(
        presentAlert: true,
        presentBadge: true,
        presentSound: true,
        sound: 'default',
        // badgeNumber: 1, // Optional
        // threadIdentifier: 'medication-reminders', // Optional
      );

      const NotificationDetails details = NotificationDetails(
        android: androidDetails,
        iOS: iosDetails,
      );

      // Schedule daily at given time
      await _notificationsPlugin.zonedSchedule(
        id,
        title,
        body,
        _nextInstanceOfTime(hour, minute),
        details,
        payload: payload,
        androidAllowWhileIdle: true,
        uiLocalNotificationDateInterpretation:
            UILocalNotificationDateInterpretation.absoluteTime,
        matchDateTimeComponents: DateTimeComponents.time,
      );

      print('Scheduled daily reminder: $title at $hour:$minute (ID: $id)');
      return id;
    } catch (e) {
      print('Error scheduling reminder: $e');
      rethrow;
    }
  }

  /// Schedule multiple time slots for a medication
  /// Schedule multiple time slots for a medication
static Future<List<int>> scheduleMedicationTimeSlots({
  required int baseId,
  required List<String> timeSlots,
  required String medicationName,
  required String dosage,
}) async {
  final List<int> scheduledIds = [];

  for (int i = 0; i < timeSlots.length; i++) {
    try {
      final timeString = timeSlots[i];
      final timeParts = timeString.split(':');
      final hour = int.parse(timeParts[0]);
      final minute = int.parse(timeParts[1]);

      final timeLabel = _getTimeOfDayLabel(hour);
      final notificationId = baseId * 100 + i; // Generate unique ID

      await scheduleDailyReminder(
        id: notificationId,
        hour: hour,
        minute: minute,
        title: 'Medication Reminder - $timeLabel',
        body: 'Time to take $medicationName${dosage.isNotEmpty ? ' ($dosage)' : ''}',
        payload: jsonEncode({
          'medicationId': baseId.toString(),
          'timeSlotIndex': i,
          'type': 'medication_reminder',
        }),
      );

      scheduledIds.add(notificationId);
    } catch (e) {
      // Use the index to get the time string for error reporting
      final errorTimeString = timeSlots[i];
      print('Error scheduling time slot $errorTimeString: $e');
    }
  }

  return scheduledIds;
}

  /// Calculate the next occurrence of a specific time
  static tz.TZDateTime _nextInstanceOfTime(int hour, int minute) {
    final now = tz.TZDateTime.now(tz.local);
    var scheduledDate = tz.TZDateTime(tz.local, now.year, now.month, now.day, hour, minute);
    
    // If the time has already passed today, schedule for tomorrow
    if (scheduledDate.isBefore(now)) {
      scheduledDate = scheduledDate.add(const Duration(days: 1));
    }
    
    return scheduledDate;
  }

  /// Get time of day label for notification
  static String _getTimeOfDayLabel(int hour) {
    if (hour < 12) return 'Morning';
    if (hour < 17) return 'Afternoon';
    if (hour < 21) return 'Evening';
    return 'Night';
  }

  /// Cancel a specific notification
  static Future<void> cancelNotification(int id) async {
    try {
      await _notificationsPlugin.cancel(id);
      print('Cancelled notification with ID: $id');
    } catch (e) {
      print('Error cancelling notification $id: $e');
    }
  }

  /// Cancel multiple notifications
  static Future<void> cancelNotifications(List<int> ids) async {
    try {
      for (final id in ids) {
        await cancelNotification(id);
      }
      print('Cancelled ${ids.length} notifications');
    } catch (e) {
      print('Error cancelling notifications: $e');
    }
  }

  /// Cancel all notifications
  static Future<void> cancelAllNotifications() async {
    try {
      await _notificationsPlugin.cancelAll();
      print('Cancelled all notifications');
    } catch (e) {
      print('Error cancelling all notifications: $e');
    }
  }

  /// Check if a notification is scheduled
  static Future<bool> isNotificationScheduled(int id) async {
    try {
      final pendingNotifications = await getPendingNotifications();
      return pendingNotifications.any((notification) => notification.id == id);
    } catch (e) {
      print('Error checking if notification is scheduled: $e');
      return false;
    }
  }

  /// Get all pending notifications
  static Future<List<PendingNotificationRequest>> getPendingNotifications() async {
    try {
      return await _notificationsPlugin.pendingNotificationRequests();
    } catch (e) {
      print('Error getting pending notifications: $e');
      return [];
    }
  }

  /// Show an immediate notification (for testing)
  static Future<void> showInstantNotification({
    required String title,
    required String body,
    String? payload,
  }) async {
    try {
      const AndroidNotificationDetails androidDetails = AndroidNotificationDetails(
        _medicationChannelId,
        _medicationChannelName,
        channelDescription: _medicationChannelDescription,
        importance: Importance.high,
        priority: Priority.high,
      );

      const DarwinNotificationDetails iosDetails = DarwinNotificationDetails(
        presentAlert: true,
        presentBadge: true,
        presentSound: true,
      );

      const NotificationDetails details = NotificationDetails(
        android: androidDetails,
        iOS: iosDetails,
      );

      await _notificationsPlugin.show(
        0, // ID 0 for instant notifications
        title,
        body,
        details,
        payload: payload,
      );
    } catch (e) {
      print('Error showing instant notification: $e');
    }
  }

  /// Handle notification tap when app is in foreground
  static void _onNotificationTap(NotificationResponse response) {
    print('Notification tapped: ${response.payload}');
    // You can handle navigation here based on the payload
    _handleNotificationPayload(response.payload);
  }

  /// Handle notification tap when app is in background
  static void _onBackgroundNotificationTap(NotificationResponse response) {
    print('Background notification tapped: ${response.payload}');
    _handleNotificationPayload(response.payload);
  }

  /// Handle notification payload
  static void _handleNotificationPayload(String? payload) {
    if (payload != null) {
      try {
        final data = jsonDecode(payload);
        if (data['type'] == 'medication_reminder') {
          final medicationId = data['medicationId'];
          final timeSlotIndex = data['timeSlotIndex'];
          print('Medication reminder tapped: ID $medicationId, slot $timeSlotIndex');
          // You can trigger navigation or mark as taken here
        }
      } catch (e) {
        print('Error handling notification payload: $e');
      }
    }
  }
}