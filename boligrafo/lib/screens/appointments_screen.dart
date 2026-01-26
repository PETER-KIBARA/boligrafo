import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/appointment_provider.dart';
import '../models/appointment_model.dart';
import 'package:intl/intl.dart';

class AppointmentsScreen extends StatefulWidget {
  const AppointmentsScreen({super.key});

  @override
  State<AppointmentsScreen> createState() => _AppointmentsScreenState();
}

class _AppointmentsScreenState extends State<AppointmentsScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      Provider.of<AppointmentProvider>(context, listen: false).fetchAppointments();
    });
  }

  @override
  Widget build(BuildContext context) {
    final appointmentProvider = Provider.of<AppointmentProvider>(context, listen: false);

    return Scaffold(
      appBar: AppBar(
        title: const Text("My Appointments"),
        backgroundColor: Colors.blue[800],
        elevation: 0,
      ),
      body: RefreshIndicator(
        onRefresh: () => appointmentProvider.fetchAppointments(),
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Consumer<AppointmentProvider>(
            builder: (context, provider, _) {
              if (provider.isLoading && provider.appointments.isEmpty) {
                return const Center(child: CircularProgressIndicator());
              }

              if (provider.appointments.isEmpty) {
                return const Center(
                  child: Text(
                    "No appointments found.",
                    style: TextStyle(fontSize: 16),
                  ),
                );
              }

              return SingleChildScrollView(
                physics: const AlwaysScrollableScrollPhysics(),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Upcoming Appointments
                    if (provider.upcomingAppointments.isNotEmpty) ...[
                      Row(
                        children: [
                          Icon(Icons.calendar_today, color: Colors.blue[800]),
                          const SizedBox(width: 8),
                          Text(
                            "Upcoming Appointments",
                            style: Theme.of(context)
                                .textTheme
                                .titleLarge
                                ?.copyWith(fontWeight: FontWeight.bold),
                          ),
                        ],
                      ),
                      const SizedBox(height: 16.0),
                      ...provider.upcomingAppointments.map(
                        (appointment) => AppointmentCard(appointment: appointment),
                      ),
                      const SizedBox(height: 24.0),
                    ],

                    // Past Appointments
                    if (provider.pastAppointments.isNotEmpty) ...[
                      Row(
                        children: [
                          Icon(Icons.history, color: Colors.grey[600]),
                          const SizedBox(width: 8),
                          Text(
                            "Past Appointments",
                            style: Theme.of(context)
                                .textTheme
                                .titleLarge
                                ?.copyWith(fontWeight: FontWeight.bold),
                          ),
                        ],
                      ),
                      const SizedBox(height: 16.0),
                      ...provider.pastAppointments.map(
                        (appointment) => AppointmentCard(appointment: appointment),
                      ),
                    ],
                  ],
                ),
              );
            },
          ),
        ),
      ),
    );
  }
}

class AppointmentCard extends StatelessWidget {
  final AppointmentModel appointment;

  const AppointmentCard({super.key, required this.appointment});

  @override
  Widget build(BuildContext context) {
    final dateFormat = DateFormat('MMM dd, yyyy');
    final isUpcoming = appointment.isUpcoming;

    Color statusColor;
    IconData statusIcon;

    switch (appointment.status) {
      case 'scheduled':
        statusColor = Colors.blue;
        statusIcon = Icons.schedule;
        break;
      case 'completed':
        statusColor = Colors.green;
        statusIcon = Icons.check_circle;
        break;
      case 'cancelled':
        statusColor = Colors.red;
        statusIcon = Icons.cancel;
        break;
      case 'missed':
        statusColor = Colors.orange;
        statusIcon = Icons.warning;
        break;
      default:
        statusColor = Colors.grey;
        statusIcon = Icons.info;
    }

    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(
          color: isUpcoming ? Colors.blue.shade200 : Colors.grey.shade200,
          width: isUpcoming ? 2 : 1,
        ),
        boxShadow: [
          BoxShadow(
            color: Colors.grey.withOpacity(0.1),
            blurRadius: 4,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Date and Time
          Row(
            children: [
              Icon(Icons.calendar_today, size: 16, color: Colors.grey[600]),
              const SizedBox(width: 8),
              Text(
                appointment.date != null
                    ? dateFormat.format(appointment.date!)
                    : 'No date',
                style: const TextStyle(
                  fontWeight: FontWeight.w600,
                  fontSize: 16,
                ),
              ),
              const SizedBox(width: 16),
              Icon(Icons.access_time, size: 16, color: Colors.grey[600]),
              const SizedBox(width: 8),
              Text(
                appointment.time ?? 'No time',
                style: const TextStyle(fontSize: 16),
              ),
            ],
          ),
          const SizedBox(height: 12),

          // Reason
          Text(
            appointment.reason,
            style: const TextStyle(
              fontSize: 14,
              color: Colors.black87,
            ),
          ),
          const SizedBox(height: 12),

          // Doctor and Status
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              if (appointment.doctorName != null)
                Row(
                  children: [
                    Icon(Icons.person, size: 16, color: Colors.grey[600]),
                    const SizedBox(width: 4),
                    Text(
                      appointment.doctorName!,
                      style: TextStyle(
                        fontSize: 13,
                        color: Colors.grey[700],
                      ),
                    ),
                  ],
                ),
              Row(
                children: [
                  Icon(statusIcon, size: 16, color: statusColor),
                  const SizedBox(width: 4),
                  Text(
                    appointment.statusDisplay,
                    style: TextStyle(
                      fontSize: 13,
                      color: statusColor,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ],
              ),
            ],
          ),
        ],
      ),
    );
  }
}
