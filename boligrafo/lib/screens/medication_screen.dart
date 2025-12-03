import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/medication_provider.dart';
import '../models/medication_service.dart';

class MedicationScreen extends StatelessWidget {
  const MedicationScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final medicationProvider = Provider.of<MedicationProvider>(context, listen: false);

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
          child: Consumer<MedicationProvider>(
            builder: (context, provider, _) {
              if (provider.isLoading) {
                return const Center(child: CircularProgressIndicator());
              }

              if (provider.medications.isEmpty) {
                return const Center(
                  child: Text(
                    "No medications found.",
                    style: TextStyle(fontSize: 16),
                  ),
                );
              }

              return SingleChildScrollView(
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
                    ...provider.medications.map(
                      (med) => MedicationCard(medicationId: med.id),
                    ),
                    const SizedBox(height: 24.0),
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

class MedicationCard extends StatefulWidget {
  final int medicationId;

  const MedicationCard({super.key, required this.medicationId});

  @override
  State<MedicationCard> createState() => _MedicationCardState();
}

class _MedicationCardState extends State<MedicationCard> {
  bool _loadingDose = false;
  bool _loadingAll = false;

  @override
  Widget build(BuildContext context) {
    return Consumer<MedicationProvider>(
      builder: (context, provider, _) {
        final med = provider.medications.firstWhere((m) => m.id == widget.medicationId);

        int takenCount = med.doses.where((d) => d.isTaken).length;
        double progress = med.doses.isEmpty ? 0 : takenCount / med.doses.length;

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
              // Medication Info
              Row(
                children: [
                  Expanded(flex: 2, child: Text(med.name, style: const TextStyle(fontWeight: FontWeight.w500, fontSize: 16))),
                  Expanded(flex: 1, child: Text(med.dosage, style: const TextStyle(fontSize: 14))),
                  Expanded(flex: 1, child: Text(med.frequency, style: const TextStyle(fontSize: 14))),
                ],
              ),
              const SizedBox(height: 12),
              Container(height: 1, color: Colors.grey.shade200),
              const SizedBox(height: 12),

              // Dose Chips
              const Text(
                "Mark as taken:",
                style: TextStyle(fontWeight: FontWeight.w500, fontSize: 14, color: Colors.grey),
              ),
              const SizedBox(height: 8),
              Wrap(
                spacing: 8,
                runSpacing: 8,
                children: med.doses.map((dose) {
                  final isTaken = dose.isTaken;
                  return GestureDetector(
                    onTap: _loadingDose || isTaken
                        ? null
                        : () async {
                            setState(() => _loadingDose = true);
                            try {
                              await provider.logDoseTaken(med.id, dose.backendKey);
                            } catch (e) {
                              ScaffoldMessenger.of(context).showSnackBar(
                                SnackBar(content: Text("Failed to log dose: $e")),
                              );
                            } finally {
                              if (mounted) setState(() => _loadingDose = false);
                            }
                          },
                    child: _buildDoseChip(dose, isTaken),
                  );
                }).toList(),
              ),
              const SizedBox(height: 12),

              // Progress Bar
              Container(
                height: 6,
                decoration: BoxDecoration(
                  color: Colors.grey.shade200,
                  borderRadius: BorderRadius.circular(3),
                ),
                child: AnimatedContainer(
                  duration: const Duration(milliseconds: 300),
                  width: MediaQuery.of(context).size.width * progress,
                  decoration: BoxDecoration(
                    color: _getProgressColor(progress),
                    borderRadius: BorderRadius.circular(3),
                  ),
                ),
              ),
              const SizedBox(height: 4),
              Text(
                "$takenCount of ${med.doses.length} doses taken today",
                style: const TextStyle(fontSize: 12, color: Colors.grey),
              ),

              const SizedBox(height: 12),
              // Mark all button
              Align(
                alignment: Alignment.centerRight,
                child: ElevatedButton(
                  onPressed: _loadingAll
                      ? null
                      : () async {
                          setState(() => _loadingAll = true);
                          try {
                            await provider.markAllDoses(med.id, true);
                          } finally {
                            if (mounted) setState(() => _loadingAll = false);
                          }
                        },
                  child: _loadingAll ? const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white)) : const Text("Mark All Taken"),
                ),
              ),
            ],
          ),
        );
      },
    );
  }

  Widget _buildDoseChip(DoseLog dose, bool isTaken) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      decoration: BoxDecoration(
        color: isTaken ? Colors.green[50] : Colors.grey[50],
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: isTaken ? Colors.green : Colors.grey.shade300, width: 1.5),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(isTaken ? Icons.check_circle : Icons.radio_button_unchecked,
              color: isTaken ? Colors.green : Colors.grey, size: 16),
          const SizedBox(width: 4),
          Text(dose.timeLabel, style: TextStyle(color: isTaken ? Colors.green : Colors.grey.shade700, fontWeight: FontWeight.w500)),
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
