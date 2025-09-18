import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'emergency_guidance_screen.dart';
import 'tips_details.dart';
import 'tips_data.dart';
import 'package:fl_chart/fl_chart.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'api/api_service.dart';
import 'medication_service.dart';

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  List<dynamic> _vitals = [];
  List<MedicationScheduleItem> _meds = [];
  bool _loading = true;
  String? _patientName;

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final token = prefs.getString('patientToken') ?? '';
      final name = prefs.getString('patientName');
      final vitals = await ApiService.fetchVitals(token);
      final meds = await MedicationService.getSchedule();
      setState(() {
        _patientName = name;
        _vitals = vitals;
        _meds = meds;
        _loading = false;
      });
    } catch (_) {
      setState(() => _loading = false);
    }
  }

  String _getGreeting() {
    final hour = DateTime.now().hour;
    if (hour < 12) {
      return "Good morning";
    } else if (hour < 17) {
      return "Good afternoon";
    } else if (hour < 20) {
      return "Good evening";
    } else {
      return "Good night";
    }
  }

  bool _isCritical(Map v) {
    final int sys = v['systolic'] ?? 0;
    final int dia = v['diastolic'] ?? 0;
    return sys >= 180 || dia >= 120;
  }

  List<FlSpot> _spots() {
    final List<FlSpot> points = [];
    for (int i = 0; i < _vitals.length; i++) {
      final v = _vitals[i] as Map<String, dynamic>;
      final y = (v['systolic'] ?? 0).toDouble();
      points.add(FlSpot(i.toDouble(), y));
    }
    return points;
  }

  Widget _buildChart() {
    if (_vitals.isEmpty) {
      return const SizedBox(
        height: 200,
        child: Center(child: Text('No data yet')),
      );
    }
    return SizedBox(
      height: 220,
      child: LineChart(
        LineChartData(
          gridData: const FlGridData(show: false),
          titlesData: const FlTitlesData(show: false),
          borderData: FlBorderData(show: true),
          lineBarsData: [
            LineChartBarData(
              spots: _spots(),
              isCurved: true,
              color: const Color(0xFF4CAF50),
              barWidth: 3,
              dotData: const FlDotData(show: false),
            )
          ],
        ),
      ),
    );
  }

  Widget _buildCriticalAlert() {
    if (_vitals.isEmpty) return const SizedBox.shrink();
    final latest = _vitals.first as Map<String, dynamic>;
    if (!_isCritical(latest)) return const SizedBox.shrink();
    return Card(
      color: Colors.red.shade50,
      child: ListTile(
        leading: const Icon(Icons.warning_amber_outlined, color: Colors.red),
        title: const Text('Critical blood pressure detected!'),
        subtitle: const Text('Consider emergency steps while awaiting help.'),
        trailing: TextButton(
          onPressed: () {
            Navigator.push(
              context,
              MaterialPageRoute(builder: (context) => const EmergencyGuidanceScreen()),
            );
          },
          child: const Text('Get Help'),
        ),
      ),
    );
  }

  Future<void> _toggleTaken(MedicationScheduleItem item, bool value) async {
    await MedicationService.setTakenToday(item.id, value);
    final updated = await MedicationService.getSchedule();
    setState(() => _meds = updated);
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) {
      return const Scaffold(body: Center(child: CircularProgressIndicator()));
    }

    final DateTime now = DateTime.now();
    final String formattedDate = DateFormat('EEEE, MMMM d').format(now);
    final String formattedTime = DateFormat('h:mm a').format(now);

    String latestBpReading = '—';
    String bpStatus = '—';
    String lastReadingTimestamp = '—';
    if (_vitals.isNotEmpty) {
      final v = _vitals.first as Map<String, dynamic>;
      latestBpReading = '${v['systolic']}/${v['diastolic']} mmHg';
      final int sys = v['systolic'] ?? 0;
      final int dia = v['diastolic'] ?? 0;
      if (sys >= 180 || dia >= 120) {
        bpStatus = 'Critical';
      } else if (sys >= 130 || dia >= 80) {
        bpStatus = 'Elevated';
      } else {
        bpStatus = 'Normal';
      }
      lastReadingTimestamp = v['created_at']?.toString() ?? 'Recent';
    }

    Color statusColor = const Color(0xFF4CAF50);
    if (bpStatus == 'Elevated') {
      statusColor = Colors.orange;
    } else if (bpStatus == 'Critical') {
      statusColor = Colors.red;
    }

    return Scaffold(
      appBar: AppBar(
        title: Text('${_patientName?.isNotEmpty == true ? _patientName : "Dashboard"}'),
        elevation: 0,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildCriticalAlert(),
            Text(
              '${_getGreeting()}, ${_patientName?.isNotEmpty == true ? _patientName : "patint"} 👋',
              style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
            ),
            const SizedBox(height: 4.0),
            Text(
              '$formattedDate | $formattedTime',
              style: Theme.of(context).textTheme.titleSmall?.copyWith(
                    color: Colors.grey[600],
                  ),
            ),
            const SizedBox(height: 24.0),
            Card(
              elevation: 2.0,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12.0),
              ),
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Blood Pressure Overview',
                      style: Theme.of(context).textTheme.titleLarge?.copyWith(
                            fontWeight: FontWeight.bold,
                          ),
                    ),
                    const SizedBox(height: 16.0),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              latestBpReading,
                              style: Theme.of(context).textTheme.displaySmall?.copyWith(
                                    color: statusColor,
                                    fontWeight: FontWeight.bold,
                                  ),
                            ),
                            const SizedBox(height: 4.0),
                            Text(
                              'Status: $bpStatus',
                              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                                    color: statusColor,
                                  ),
                            ),
                          ],
                        ),
                        Column(
                          crossAxisAlignment: CrossAxisAlignment.end,
                          children: [
                            Text(
                              'Last Reading:',
                              style: Theme.of(context).textTheme.titleSmall?.copyWith(
                                    color: Colors.grey[600],
                                  ),
                            ),
                            const SizedBox(height: 4.0),
                            Text(
                              lastReadingTimestamp,
                              style: Theme.of(context).textTheme.titleSmall,
                            ),
                          ],
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ),

            Text(
              'Todays Medications',
              style: Theme.of(context).textTheme.titleLarge?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
            ),
            const SizedBox(height: 16.0),
            ListView.builder(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              itemCount: _meds.length,
              itemBuilder: (context, index) {
                final medication = _meds[index];
                return Card(
                  elevation: 1.0,
                  margin: const EdgeInsets.only(bottom: 8.0),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(8.0),
                  ),
                  child: Padding(
                    padding: const EdgeInsets.all(12.0),
                    child: Row(
                      children: [
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                medication.name,
                                style: Theme.of(context).textTheme.titleMedium,
                              ),
                              const SizedBox(height: 4.0),
                              Text(
                                medication.time,
                                style: Theme.of(context).textTheme.titleSmall?.copyWith(
                                      color: Colors.grey[600],
                                    ),
                              ),
                            ],
                          ),
                        ),
                        Checkbox(
                          value: medication.takenToday,
                          onChanged: (bool? value) {
                            if (value == null) return;
                            _toggleTaken(medication, value);
                          },
                        ),
                      ],
                    ),
                  ),
                );
              },
            ),
            const SizedBox(height: 24.0),
            Text(
              'Trends & Progress',
              style: Theme.of(context).textTheme.titleLarge?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
            ),
            const SizedBox(height: 16.0),
            Card(
              elevation: 2.0,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12.0),
              ),
              child: Padding(
                padding: const EdgeInsets.all(12.0),
                child: _buildChart(),
              ),
            ),

            Text(
              'Lifestyle Tips',
              style: Theme.of(context).textTheme.titleLarge?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
            ),
            const SizedBox(height: 16.0),
            SizedBox(
              height: 160.0,
              child: ListView.builder(
                scrollDirection: Axis.horizontal,
                itemCount: lifestyleTips.length,
                itemBuilder: (context, index) {
                  final tip = lifestyleTips[index];
                  return GestureDetector(
                    onTap: () {
                      Navigator.push(
                        context,
                        MaterialPageRoute(
                          builder: (context) => LifestyleTipDetailScreen(tipId: tip.id),
                        ),
                      );
                    },
                    child: Card(
                      elevation: 2.0,
                      color: Colors.greenAccent,
                      margin: const EdgeInsets.only(right: 12.0),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12.0),
                      ),
                      child: Container(
                        width: 200.0,
                        padding: const EdgeInsets.all(12.0),
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Text(
                              'Tip #${tip.id}',
                              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                                    fontWeight: FontWeight.bold,
                                    color: Colors.black54,
                                  ),
                            ),
                            const SizedBox(height: 8),
                            Text(
                              tip.title,
                              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                                    fontSize: 16,
                                    fontWeight: FontWeight.w600,
                                  ),
                              textAlign: TextAlign.center,
                              maxLines: 2,
                              overflow: TextOverflow.ellipsis,
                            ),
                          ],
                        ),
                      ),
                    ),
                  );
                },
              ),
            ),
            
          ],
        ),
      ),
    );
  }
}
