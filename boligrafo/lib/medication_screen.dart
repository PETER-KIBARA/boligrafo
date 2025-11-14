import 'package:flutter/material.dart';
import 'package:myapp/medication_service.dart';
import 'package:provider/provider.dart';
import '../providers/medication_provider.dart';

class MedicationScreen extends StatelessWidget {
  const MedicationScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final medicationProvider = Provider.of<MedicationProvider>(context);

    return Scaffold(
      appBar: AppBar(
        title: const Text("My Medications"),
        backgroundColor: Colors.blue[800],
        elevation: 0,
      ),
      body: RefreshIndicator(
        onRefresh: () => medicationProvider.loadMedications(),
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: medicationProvider.isLoading
              ? const Center(child: CircularProgressIndicator())
              : medicationProvider.medications.isEmpty
                  ? const Center(
                      child: Text(
                        "No medications found.",
                        style: TextStyle(fontSize: 16),
                      ),
                    )
                  : SingleChildScrollView(
                      physics: const AlwaysScrollableScrollPhysics(),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              Icon(Icons.medication, color: Colors.blue[800]),
                              const SizedBox(width: 8),
                              Text(
                                "Today's Medications",
                                style: Theme.of(context)
                                    .textTheme
                                    .titleLarge
                                    ?.copyWith(fontWeight: FontWeight.bold),
                              ),
                            ],
                          ),
                          const SizedBox(height: 16.0),

                          // Header
                          Container(
                            decoration: BoxDecoration(
                              color: Colors.blue[50],
                              borderRadius: BorderRadius.circular(8),
                            ),
                            padding: const EdgeInsets.all(12),
                            child: const Row(
                              children: [
                                Expanded(
                                  flex: 2,
                                  child: Text(
                                    "Medication",
                                    style: TextStyle(
                                      fontWeight: FontWeight.bold,
                                    ),
                                  ),
                                ),
                                Expanded(
                                  flex: 1,
                                  child: Text(
                                    "Dosage",
                                    style: TextStyle(
                                      fontWeight: FontWeight.bold,
                                    ),
                                  ),
                                ),
                                Expanded(
                                  flex: 1,
                                  child: Text(
                                    "Frequency",
                                    style: TextStyle(
                                      fontWeight: FontWeight.bold,
                                    ),
                                  ),
                                ),
                                Expanded(
                                  flex: 2,
                                  child: Text(
                                    "Taken Today",
                                    style: TextStyle(
                                      fontWeight: FontWeight.bold,
                                    ),
                                  ),
                                ),
                              ],
                            ),
                          ),

                          const SizedBox(height: 8),

                          // Medication Rows
                          ...medicationProvider.medications.map((med) {
                            return MedicationCard(medication: med);
                          }).toList(),

                          const SizedBox(height: 24.0),
                        ],
                      ),
                    ),
        ),
      ),
    );
  }
}

class MedicationCard extends StatefulWidget {
  final MedicationScheduleItem medication;

  const MedicationCard({super.key, required this.medication});

  @override
  State<MedicationCard> createState() => _MedicationCardState();
}

class _MedicationCardState extends State<MedicationCard> {
  // Define time slots based on frequency
  List<TimeSlot> getTimeSlots() {
    final frequency = widget.medication.frequency?.toLowerCase() ?? '';
    
    if (frequency.contains('3') || frequency.contains('three') || 
        frequency.contains('tid') || frequency.contains('three times')) {
      return [
        TimeSlot('Morning', TimeOfDay(hour: 8, minute: 0)),
        TimeSlot('Afternoon', TimeOfDay(hour: 14, minute: 0)),
        TimeSlot('Evening', TimeOfDay(hour: 20, minute: 0)),
      ];
    } else if (frequency.contains('2') || frequency.contains('two') || 
               frequency.contains('bid') || frequency.contains('twice')) {
      return [
        TimeSlot('Morning', TimeOfDay(hour: 8, minute: 0)),
        TimeSlot('Evening', TimeOfDay(hour: 20, minute: 0)),
      ];
    } else if (frequency.contains('1') || frequency.contains('one') || 
               frequency.contains('once') || frequency.contains('daily')) {
      return [
        TimeSlot('Daily', TimeOfDay(hour: 12, minute: 0)),
      ];
    } else if (frequency.contains('4') || frequency.contains('four') || 
               frequency.contains('qid')) {
      return [
        TimeSlot('Morning', TimeOfDay(hour: 8, minute: 0)),
        TimeSlot('Noon', TimeOfDay(hour: 12, minute: 0)),
        TimeSlot('Evening', TimeOfDay(hour: 18, minute: 0)),
        TimeSlot('Night', TimeOfDay(hour: 22, minute: 0)),
      ];
    } else {
      // Default to once daily if frequency is not recognized
      return [
        TimeSlot('Daily', TimeOfDay(hour: 12, minute: 0)),
      ];
    }
  }

  @override
  Widget build(BuildContext context) {
    final timeSlots = getTimeSlots();
    
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(
          color: Colors.grey.shade200,
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
          // Basic medication info row
          Row(
            children: [
              Expanded(
                flex: 2,
                child: Text(
                  widget.medication.name,
                  style: const TextStyle(
                    fontWeight: FontWeight.w500,
                    fontSize: 16,
                  ),
                ),
              ),
              Expanded(
                flex: 1,
                child: Text(
                  widget.medication.dosage ?? '-',
                  style: const TextStyle(fontSize: 14),
                ),
              ),
              Expanded(
                flex: 1,
                child: Text(
                  widget.medication.frequency ?? '-',
                  style: const TextStyle(fontSize: 14),
                ),
              ),
            ],
          ),
          
          const SizedBox(height: 12),
          
          // Divider
          Container(
            height: 1,
            color: Colors.grey.shade200,
          ),
          
          const SizedBox(height: 12),
          
          // Time slots for tracking
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                "Mark as taken:",
                style: TextStyle(
                  fontWeight: FontWeight.w500,
                  fontSize: 14,
                  color: Colors.grey,
                ),
              ),
              const SizedBox(height: 8),
              
              Wrap(
                spacing: 8,
                runSpacing: 8,
                children: timeSlots.map((timeSlot) {
                  final isTaken = timeSlot.isTaken;
                  return GestureDetector(
                    onTap: () {
                      setState(() {
                        timeSlot.isTaken = !isTaken;
                      });
                    },
                    child: Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 12,
                        vertical: 8,
                      ),
                      decoration: BoxDecoration(
                        color: isTaken ? Colors.green[50] : Colors.grey[50],
                        borderRadius: BorderRadius.circular(20),
                        border: Border.all(
                          color: isTaken ? Colors.green : Colors.grey.shade300,
                          width: 1.5,
                        ),
                      ),
                      child: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Icon(
                            isTaken ? Icons.check_circle : Icons.radio_button_unchecked,
                            color: isTaken ? Colors.green : Colors.grey,
                            size: 16,
                          ),
                          const SizedBox(width: 4),
                          Text(
                            timeSlot.label,
                            style: TextStyle(
                              color: isTaken ? Colors.green : Colors.grey.shade700,
                              fontWeight: FontWeight.w500,
                            ),
                          ),
                        ],
                      ),
                    ),
                  );
                }).toList(),
              ),
              
              // Progress indicator
              const SizedBox(height: 12),
              Container(
                height: 6,
                decoration: BoxDecoration(
                  color: Colors.grey.shade200,
                  borderRadius: BorderRadius.circular(3),
                ),
                child: Stack(
                  children: [
                    LayoutBuilder(
                      builder: (context, constraints) {
                        final takenCount = timeSlots.where((slot) => slot.isTaken).length;
                        final progress = takenCount / timeSlots.length;
                        return AnimatedContainer(
                          duration: const Duration(milliseconds: 300),
                          width: constraints.maxWidth * progress,
                          decoration: BoxDecoration(
                            color: _getProgressColor(progress),
                            borderRadius: BorderRadius.circular(3),
                          ),
                        );
                      },
                    ),
                  ],
                ),
              ),
              
              const SizedBox(height: 4),
              Text(
                "${timeSlots.where((slot) => slot.isTaken).length} of ${timeSlots.length} doses taken today",
                style: const TextStyle(
                  fontSize: 12,
                  color: Colors.grey,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Color _getProgressColor(double progress) {
    if (progress == 0) return Colors.grey;
    if (progress < 0.5) return Colors.orange;
    if (progress < 1.0) return Colors.blue;
    return Colors.green;
  }
}

class TimeSlot {
  final String label;
  final TimeOfDay time;
  bool isTaken;

  TimeSlot(this.label, this.time, {this.isTaken = false});
}