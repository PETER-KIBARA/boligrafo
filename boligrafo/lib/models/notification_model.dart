class NotificationModel {
  final int id;
  final String title;
  final String message;
  final String notificationType;
  final bool isRead;
  final DateTime createdAt;
  final int? bpSystolic;
  final int? bpDiastolic;
  final String? patientName;
  final String? doctorName;

  NotificationModel({
    required this.id,
    required this.title,
    required this.message,
    required this.notificationType,
    required this.isRead,
    required this.createdAt,
    this.bpSystolic,
    this.bpDiastolic,
    this.patientName,
    this.doctorName,
  });

  factory NotificationModel.fromJson(Map<String, dynamic> json) {
    return NotificationModel(
      id: json['id'],
      title: json['title'] ?? '',
      message: json['message'] ?? '',
      notificationType: json['notification_type'] ?? 'general',
      isRead: json['is_read'] ?? false,
      createdAt: DateTime.parse(json['created_at']),
      bpSystolic: json['bp_systolic'],
      bpDiastolic: json['bp_diastolic'],
      patientName: json['patient_name'],
      doctorName: json['doctor_name'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'title': title,
      'message': message,
      'notification_type': notificationType,
      'is_read': isRead,
      'created_at': createdAt.toIso8601String(),
      'bp_systolic': bpSystolic,
      'bp_diastolic': bpDiastolic,
      'patient_name': patientName,
      'doctor_name': doctorName,
    };
  }
}
