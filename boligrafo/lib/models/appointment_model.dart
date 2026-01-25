class AppointmentModel {
  final int id;
  final int patientId;
  final String patientName;
  final int? doctorId;
  final String? doctorName;
  final DateTime? date;
  final String? time;
  final String reason;
  final String status;
  final DateTime createdAt;

  AppointmentModel({
    required this.id,
    required this.patientId,
    required this.patientName,
    this.doctorId,
    this.doctorName,
    this.date,
    this.time,
    required this.reason,
    required this.status,
    required this.createdAt,
  });

  factory AppointmentModel.fromJson(Map<String, dynamic> json) {
    return AppointmentModel(
      id: json['id'],
      patientId: json['patient'],
      patientName: json['patient_name'] ?? '',
      doctorId: json['doctor'],
      doctorName: json['doctor_name'],
      date: json['date'] != null ? DateTime.parse(json['date']) : null,
      time: json['time'],
      reason: json['reason'] ?? 'Follow-up',
      status: json['status'] ?? 'scheduled',
      createdAt: DateTime.parse(json['created_at']),
    );
  }

  String get statusDisplay {
    switch (status) {
      case 'scheduled':
        return 'Scheduled';
      case 'completed':
        return 'Completed';
      case 'cancelled':
        return 'Cancelled';
      case 'missed':
        return 'Missed';
      default:
        return status;
    }
  }

  bool get isUpcoming {
    if (date == null) return false;
    return date!.isAfter(DateTime.now()) && status == 'scheduled';
  }
}
