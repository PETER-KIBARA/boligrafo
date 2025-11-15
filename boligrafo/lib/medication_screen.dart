import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/medication_provider.dart';
import '../medication_service.dart';

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
                          ...medicationProvider.medications.map(
                            (med) => MedicationCard(medication: med),
                          ),
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
  bool _loadingDose = false;

  @override
  Widget build(BuildContext context) {
    final provider = Provider.of<MedicationProvider>(context, listen: false);

    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.grey.shade200),
        boxShadow: [
          BoxShadow(
            color: Colors.grey.withOpacity(0.05),
            blurRadius: 4,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Medication basic info
          Row(
            children: [
              Expanded(
                flex: 2,
                child: Text(
                  widget.medication.name,
                  style: const TextStyle(
                      fontWeight: FontWeight.w500, fontSize: 16),
                ),
              ),
              Expanded(
                flex: 1,
                child: Text(widget.medication.dosage,
                    style: const TextStyle(fontSize: 14)),
              ),
              Expanded(
                flex: 1,
                child: Text(widget.medication.frequency,
                    style: const TextStyle(fontSize: 14)),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Container(height: 1, color: Colors.grey.shade200),
          const SizedBox(height: 12),

          // Doses
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
      children: widget.medication.doses.map((dose) {
        final isTaken = dose.isTaken;
        return GestureDetector(
          onTap: _loadingDose
              ? null
              : () async {
                  if (isTaken) return;
                  setState(() => _loadingDose = true);

                  final messenger = ScaffoldMessenger.of(context);
                  try {
                    // Since provider returns void, we assume success unless an exception occurs
                    await provider.logDoseTaken(
                        widget.medication.id, dose.backendKey);

                    if (!mounted) return;
                    
                    // If we reach here without exception, assume success
                    setState(() {}); // refresh card UI
                    
                  } catch (e) {
                    if (!mounted) return;
                    messenger.showSnackBar(
                      SnackBar(content: Text("Failed to log dose: $e")),
                    );
                  } finally {
                    if (mounted) setState(() => _loadingDose = false);
                  }
                },
          child: Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
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
                  isTaken
                      ? Icons.check_circle
                      : Icons.radio_button_unchecked,
                  color: isTaken ? Colors.green : Colors.grey,
                  size: 16,
                ),
                const SizedBox(width: 4),
                Text(
                  dose.timeLabel,
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

    const SizedBox(height: 12),

    // Progress bar
    Container(
      height: 6,
      decoration: BoxDecoration(
        color: Colors.grey.shade200,
        borderRadius: BorderRadius.circular(3),
      ),
      child: LayoutBuilder(
        builder: (context, constraints) {
          final takenCount =
              widget.medication.doses.where((d) => d.isTaken).length;
          final progress = widget.medication.doses.isEmpty 
              ? 0.0 // Changed to double
              : takenCount / widget.medication.doses.length;
          return AnimatedContainer(
            duration: const Duration(milliseconds: 300),
            width: constraints.maxWidth * progress.toDouble(), // Convert to double
            decoration: BoxDecoration(
              color: _getProgressColor(progress.toDouble()), // Convert to double
              borderRadius: BorderRadius.circular(3),
            ),
          );
        },
      ),
    ),
    const SizedBox(height: 4),
    Text(
      "${widget.medication.doses.where((d) => d.isTaken).length} of ${widget.medication.doses.length} doses taken today",
      style: const TextStyle(fontSize: 12, color: Colors.grey),
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
