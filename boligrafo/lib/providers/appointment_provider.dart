import 'package:flutter/material.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/appointment_model.dart';
import '../models/notifications_service.dart';

class AppointmentProvider with ChangeNotifier {
  final String apiBaseUrl;
  final String token;

  List<AppointmentModel> _appointments = [];
  bool _isLoading = false;

  AppointmentProvider({
    required this.apiBaseUrl,
    required this.token,
  });

  List<AppointmentModel> get appointments => _appointments;
  bool get isLoading => _isLoading;
  
  List<AppointmentModel> get upcomingAppointments =>
      _appointments.where((a) => a.isUpcoming).toList();
  
  List<AppointmentModel> get pastAppointments =>
      _appointments.where((a) => !a.isUpcoming).toList();

  /// Fetch appointments from backend
  Future<void> fetchAppointments() async {
    _isLoading = true;
    notifyListeners();

    try {
      final url = Uri.parse('$apiBaseUrl/appointments/my/');
      final response = await http.get(
        url,
        headers: {
          'Authorization': 'Token $token',
          'Content-Type': 'application/json',
        },
      );

      if (response.statusCode == 200) {
        final List<dynamic> data = jsonDecode(response.body);
        _appointments = data
            .map((json) => AppointmentModel.fromJson(json))
            .toList();
        
        // Schedule local notifications for upcoming appointments
        await _scheduleAppointmentReminders();
      }
    } catch (e) {
      print('Error fetching appointments: $e');
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  /// Schedule local notifications for upcoming appointments
  Future<void> _scheduleAppointmentReminders() async {
    for (var appointment in upcomingAppointments) {
      if (appointment.date != null && appointment.time != null) {
        // Parse time
        final timeParts = appointment.time!.split(':');
        final hour = int.parse(timeParts[0]);
        final minute = int.parse(timeParts[1]);
        
        // Schedule notification 1 hour before appointment
        final appointmentDateTime = DateTime(
          appointment.date!.year,
          appointment.date!.month,
          appointment.date!.day,
          hour,
          minute,
        );
        
        final reminderTime = appointmentDateTime.subtract(const Duration(hours: 1));
        
        // Only schedule if reminder time is in the future
        if (reminderTime.isAfter(DateTime.now())) {
          await NotificationsService.scheduleDailyReminder(
            id: 10000 + appointment.id, // Use unique ID range for appointments
            hour: reminderTime.hour,
            minute: reminderTime.minute,
            title: 'Upcoming Appointment',
            body: 'You have an appointment in 1 hour: ${appointment.reason}',
            payload: jsonEncode({
              'type': 'appointment_reminder',
              'appointment_id': appointment.id,
            }),
          );
        }
      }
    }
  }
}
