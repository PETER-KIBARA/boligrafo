import 'package:flutter/material.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/notification_model.dart';

class NotificationProvider with ChangeNotifier {
  final String apiBaseUrl;
  final String token;

  List<NotificationModel> _notifications = [];
  bool _isLoading = false;

  NotificationProvider({
    required this.apiBaseUrl,
    required this.token,
  });

  List<NotificationModel> get notifications => _notifications;
  bool get isLoading => _isLoading;
  
  List<NotificationModel> get unreadNotifications =>
      _notifications.where((n) => !n.isRead).toList();
  
  int get unreadCount => unreadNotifications.length;

  /// Fetch notifications from backend
  Future<void> fetchNotifications() async {
    _isLoading = true;
    notifyListeners();

    try {
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
        _notifications = data
            .map((json) => NotificationModel.fromJson(json))
            .toList();
      }
    } catch (e) {
      print('Error fetching notifications: $e');
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  /// Mark a notification as read
  Future<void> markAsRead(int notificationId) async {
    try {
      final url = Uri.parse('$apiBaseUrl/notifications/$notificationId/');
      final response = await http.patch(
        url,
        headers: {
          'Authorization': 'Token $token',
          'Content-Type': 'application/json',
        },
        body: jsonEncode({'is_read': true}),
      );

      if (response.statusCode == 200) {
        // Update local state
        final index = _notifications.indexWhere((n) => n.id == notificationId);
        if (index != -1) {
          _notifications[index] = NotificationModel.fromJson(
            jsonDecode(response.body),
          );
          notifyListeners();
        }
      }
    } catch (e) {
      print('Error marking notification as read: $e');
    }
  }

  /// Mark all notifications as read
  Future<void> markAllAsRead() async {
    for (var notification in unreadNotifications) {
      await markAsRead(notification.id);
    }
  }
}
