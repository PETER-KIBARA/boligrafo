import 'dart:async';
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import '../models/notification_model.dart';
import '../models/notifications_service.dart';

class NotificationPollingService {
  static const String _lastNotificationIdKey = 'last_notification_id';
  static const Duration _pollingInterval = Duration(minutes: 1);
  
  final String apiBaseUrl;
  final String token;
  Timer? _pollingTimer;
  
  NotificationPollingService({
    required this.apiBaseUrl,
    required this.token,
  });

  /// Start polling for notifications
  void startPolling() {
    // Poll immediately on start
    _pollNotifications();
    
    // Then poll every 5 minutes
    _pollingTimer = Timer.periodic(_pollingInterval, (_) {
      _pollNotifications();
    });
  }

  /// Stop polling
  void stopPolling() {
    _pollingTimer?.cancel();
    _pollingTimer = null;
  }

  /// Poll the backend for new notifications
  Future<void> _pollNotifications() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final lastNotificationId = prefs.getInt(_lastNotificationIdKey) ?? 0;
      
      // Fetch notifications from backend
      final url = Uri.parse('$apiBaseUrl/notifications/');
      final response = await http.get(
        url,
        headers: {
          'Authorization': 'Token $token',
          'Content-Type': 'application/json',
        },
      );

      if (response.statusCode == 200) {
        final List<dynamic> data = jsonDecode(response.body);
        final notifications = data
            .map((json) => NotificationModel.fromJson(json))
            .toList();

        // Filter for new unread notifications
        final newNotifications = notifications
            .where((n) => n.id > lastNotificationId && !n.isRead)
            .toList();

        if (newNotifications.isNotEmpty) {
          // Show local notifications for each new item
          for (var notification in newNotifications) {
            await _showLocalNotification(notification);
          }

          // Update last seen notification ID
          final maxId = notifications.map((n) => n.id).reduce((a, b) => a > b ? a : b);
          await prefs.setInt(_lastNotificationIdKey, maxId);
        }
      }
    } catch (e) {
      print('Error polling notifications: $e');
    }
  }

  /// Show a local status bar notification
  Future<void> _showLocalNotification(NotificationModel notification) async {
    await NotificationsService.showInstantNotification(
      id: notification.id,
      title: notification.title,
      body: notification.message,
      payload: jsonEncode({
        'type': 'backend_notification',
        'notification_id': notification.id,
      }),
    );
  }
}
