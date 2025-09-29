import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'emergency_guidance_screen.dart';
import 'tips_details.dart';
import 'tips_data.dart';
import 'package:fl_chart/fl_chart.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'api/api_service.dart';
import 'medication_service.dart';
import 'dart:async';

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  List<dynamic> _vitals = [];
  List<MedicationScheduleItem> _meds = [];
  //List<Map<String, dynamic>> _aiTips = [];
  bool _loading = true;
  String? _patientName;

  Timer? _refreshTimer;

@override
void initState() {
  super.initState();
  _loadData();

  _refreshTimer = Timer.periodic(const Duration(seconds: 30), (_) {
    _loadData();
  });
}

@override
void dispose() {
  _refreshTimer?.cancel(); // Clean up timer when screen is closed
  super.dispose();
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
      return Container(
        height: 200,
        decoration: BoxDecoration(
          color: Colors.grey[50],
          borderRadius: BorderRadius.circular(12),
        ),
        child: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(Icons.show_chart, size: 40, color: Colors.grey[300]),
              const SizedBox(height: 8),
              Text('No data available yet',
                  style: TextStyle(color: Colors.grey[500])),
            ],
          ),
        ),
      );
    }
    return SizedBox(
      height: 220,
      child: LineChart(
        LineChartData(
          gridData: FlGridData(
            show: true,
            drawVerticalLine: false,
            horizontalInterval: 20,
            getDrawingHorizontalLine: (value) => FlLine(
              color: Colors.grey[200],
              strokeWidth: 1,
            ),
          ),
          titlesData: FlTitlesData(
            bottomTitles: AxisTitles(
              sideTitles: SideTitles(showTitles: false),
            ),
            leftTitles: AxisTitles(
              sideTitles: SideTitles(
                showTitles: true,
                interval: 20,
                reservedSize: 40,
                getTitlesWidget: (value, meta) {
                  return Text(value.toInt().toString(),
                      style: TextStyle(
                        fontSize: 10,
                        color: Colors.grey[600],
                      ));
                },
              ),
            ),
            rightTitles: AxisTitles(sideTitles: SideTitles(showTitles: false)),
            topTitles: AxisTitles(sideTitles: SideTitles(showTitles: false)),
          ),
          borderData: FlBorderData(
            show: true,
            border: Border.all(color: Colors.grey[300]!, width: 1),
          ),
          minX: 0,
          maxX: _vitals.length > 1 ? (_vitals.length - 1).toDouble() : 1,
          minY: 0,
          maxY: _vitals.isNotEmpty
              ? (_vitals.map((v) => (v['systolic'] ?? 0).toDouble()).reduce(
                      (a, b) => a > b ? a : b) *
                  1.1)
              : 200,
          lineBarsData: [
            LineChartBarData(
              spots: _spots(),
              isCurved: true,
              color: const Color(0xFF4CAF50),
              gradient: const LinearGradient(
                colors: [Color(0xFF4CAF50), Color(0xFF8BC34A)],
                begin: Alignment.topCenter,
                end: Alignment.bottomCenter,
              ),
              barWidth: 4,
              belowBarData: BarAreaData(
                show: true,
                gradient: LinearGradient(
                  colors: [
                    // ignore: deprecated_member_use
                    const Color(0xFF4CAF50).withOpacity(0.3),
                    // ignore: deprecated_member_use
                    const Color(0xFF4CAF50).withOpacity(0.1),
                  ],
                ),
              ),
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
    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      decoration: BoxDecoration(
        color: Colors.red.shade50,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.red.shade100),
      ),
      child: ListTile(
        leading: Container(
          padding: const EdgeInsets.all(8),
          decoration: BoxDecoration(
            color: Colors.red.shade100,
            shape: BoxShape.circle,
          ),
          child: const Icon(Icons.warning_amber_rounded, color: Colors.red),
        ),
        title: Text('Critical blood pressure detected!',
            style: TextStyle(
                fontWeight: FontWeight.bold, color: Colors.red[800])),
        subtitle: Text('Consider emergency steps while awaiting help.',
            style: TextStyle(color: Colors.red[700])),
        trailing: ElevatedButton.icon(
          onPressed: () {
            Navigator.push(
              context,
              MaterialPageRoute(
                  builder: (context) => const EmergencyGuidanceScreen()),
            );
          },
          icon: const Icon(Icons.emergency, size: 16),
          label: const Text('Get Help'),
          style: ElevatedButton.styleFrom(
            backgroundColor: Colors.red,
            foregroundColor: Colors.white,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(20),
            ),
          ),
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
      return Scaffold(
        body: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const CircularProgressIndicator(),
              const SizedBox(height: 16),
              Text('Loading your health data...',
                  style: TextStyle(color: Colors.grey[600])),
            ],
          ),
        ),
      );
    }

    final DateTime now = DateTime.now();
    final String formattedDate = DateFormat('EEEE, MMMM d').format(now);
    final String formattedTime = DateFormat('h:mm a').format(now);

    String latestBpReading = '—';
    String bpStatus = '—';
    String lastReadingTimestamp = '—';
    if (_vitals.isNotEmpty) {
  // Sort vitals by created_at just to be safe
  _vitals.sort((a, b) {
    final da = DateTime.tryParse(a['created_at'] ?? '') ?? DateTime(1970);
    final db = DateTime.tryParse(b['created_at'] ?? '') ?? DateTime(1970);
    return da.compareTo(db); // oldest → newest
  });

  final v = _vitals.last as Map<String, dynamic>; // latest reading

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
        title: Text(
            '${_patientName?.isNotEmpty == true ? _patientName : "Dashboard"}'),
        elevation: 0,
        backgroundColor: Colors.white,
        foregroundColor: Colors.blue[800],
        centerTitle: false,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildCriticalAlert(),
            
            // Welcome Section
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.blue[50],
                borderRadius: BorderRadius.circular(12),
              ),
              child: Row(
                children: [
                  CircleAvatar(
                    backgroundColor: Colors.blue[100],
                    child: Icon(Icons.person, color: Colors.blue[800]),
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          '${_getGreeting()}, ${_patientName?.isNotEmpty == true ? _patientName : "Patient"} 👋',
                          style: Theme.of(context)
                              .textTheme
                              .titleLarge
                              ?.copyWith(
                                fontWeight: FontWeight.bold,
                                color: Colors.blue[900],
                              ),
                        ),
                        const SizedBox(height: 4.0),
                        Text(
                          '$formattedDate | $formattedTime',
                          style: TextStyle(
                            color: Colors.blue[700],
                            fontSize: 14,
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
            
            const SizedBox(height: 24.0),
            
            // Blood Pressure Card
            Card(
              elevation: 4,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(16.0),
              ),
              child: Container(
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                    colors: [
                      Colors.blue[50]!,
                      Colors.white,
                    ],
                  ),
                  borderRadius: BorderRadius.circular(16),
                ),
                child: Padding(
                  padding: const EdgeInsets.all(20.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Icon(Icons.monitor_heart,
                              color: Colors.blue[800], size: 24),
                          const SizedBox(width: 8),
                          Text(
                            'Blood Pressure',
                            style: Theme.of(context)
                                .textTheme
                                .titleLarge
                                ?.copyWith(
                                  fontWeight: FontWeight.bold,
                                  color: Colors.blue[900],
                                ),
                          ),
                        ],
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
                                style: Theme.of(context)
                                    .textTheme
                                    .displaySmall
                                    ?.copyWith(
                                      color: statusColor,
                                      fontWeight: FontWeight.bold,
                                    ),
                              ),
                              const SizedBox(height: 8.0),
                              Container(
                                padding: const EdgeInsets.symmetric(
                                    horizontal: 12, vertical: 6),
                                decoration: BoxDecoration(
                                  color: statusColor.withOpacity(0.1),
                                  borderRadius: BorderRadius.circular(20),
                                ),
                                child: Text(
                                  bpStatus,
                                  style: TextStyle(
                                    color: statusColor,
                                    fontWeight: FontWeight.w600,
                                  ),
                                ),
                              ),
                            ],
                          ),
                          Column(
                            crossAxisAlignment: CrossAxisAlignment.end,
                            children: [
                              Text(
                                'Last Reading',
                                style: TextStyle(
                                  color: Colors.grey[600],
                                  fontSize: 12,
                                ),
                              ),
                              const SizedBox(height: 4.0),
                              Text(
                                lastReadingTimestamp,
                                style: const TextStyle(
                                  fontWeight: FontWeight.w500,
                                ),
                              ),
                            ],
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              ),
            ),

            const SizedBox(height: 24.0),
            
            // Medications Section
            Row(
              children: [
                Icon(Icons.medication, color: Colors.blue[800]),
                const SizedBox(width: 8),
                Text(
                  "Today's Medications",
                  style: Theme.of(context).textTheme.titleLarge?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                ),
              ],
            ),
            const SizedBox(height: 16.0),
            ..._meds.map((medication) {
              return Container(
                margin: const EdgeInsets.only(bottom: 12),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(12),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.grey.withOpacity(0.1),
                      blurRadius: 8,
                      offset: const Offset(0, 2),
                    ),
                  ],
                ),
                child: ListTile(
                  leading: Container(
                    padding: const EdgeInsets.all(8),
                    decoration: BoxDecoration(
                      color: Colors.blue[50],
                      shape: BoxShape.circle,
                    ),
                    child: Icon(Icons.medication_liquid,
                        color: Colors.blue[800], size: 20),
                  ),
                  title: Text(
                    medication.name,
                    style: const TextStyle(fontWeight: FontWeight.w600),
                  ),
                  subtitle: Text(
                    medication.time,
                    style: TextStyle(color: Colors.grey[600]),
                  ),
                  trailing: Transform.scale(
                    scale: 1.2,
                    child: Switch(
                      value: medication.takenToday,
                      onChanged: (bool value) {
                        _toggleTaken(medication, value);
                      },
                      activeColor: Colors.green,
                    ),
                  ),
                ),
              );
            }).toList(),
            
            const SizedBox(height: 24.0),
            
            // Trends Section
            Row(
              children: [
                Icon(Icons.trending_up, color: Colors.blue[800]),
                const SizedBox(width: 8),
                Text(
                  'Trends & Progress',
                  style: Theme.of(context).textTheme.titleLarge?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                ),
              ],
            ),
            const SizedBox(height: 16.0),
            Card(
              elevation: 2.0,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(16.0),
              ),
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  children: [
                    Row(
                      children: [
                        Icon(Icons.show_chart, color: Colors.green[700]),
                        const SizedBox(width: 8),
                        Text(
                          'Blood Pressure Trend',
                          style: TextStyle(
                            fontWeight: FontWeight.w600,
                            color: Colors.grey[700],
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 16),
                    _buildChart(),
                  ],
                ),
              ),
            ),

            const SizedBox(height: 24.0),
            
            // Tips Section
            Row(
              children: [
                Icon(Icons.lightbulb_outline, color: Colors.blue[800]),
                const SizedBox(width: 8),
                Text(
                  'Lifestyle Tips',
                  style: Theme.of(context).textTheme.titleLarge?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                ),
              ],
            ),
            const SizedBox(height: 16.0),
            SizedBox(
              height: 180.0,
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
                          builder: (context) =>
                              LifestyleTipDetailScreen(tipId: tip.id),
                        ),
                      );
                    },
                    child: Container(
                      width: 200.0,
                      margin: const EdgeInsets.only(right: 16.0),
                      decoration: BoxDecoration(
                        gradient: LinearGradient(
                          begin: Alignment.topLeft,
                          end: Alignment.bottomRight,
                          colors: [
                            Colors.green[50]!,
                            Colors.lightGreen[100]!,
                          ],
                        ),
                        borderRadius: BorderRadius.circular(16.0),
                        boxShadow: [
                          BoxShadow(
                            color: Colors.green.withOpacity(0.1),
                            blurRadius: 8,
                            offset: const Offset(0, 4),
                          ),
                        ],
                      ),
                      child: Padding(
                        padding: const EdgeInsets.all(16.0),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Container(
                              padding: const EdgeInsets.all(6),
                              decoration: BoxDecoration(
                                color: Colors.green[100],
                                borderRadius: BorderRadius.circular(8),
                              ),
                              child: Icon(Icons.lightbulb,
                                  size: 20, color: Colors.green[800]),
                            ),
                            const SizedBox(height: 12),
                            Text(
                              tip.title,
                              style: const TextStyle(
                                fontSize: 14,
                                fontWeight: FontWeight.w600,
                                color: Colors.green,
                              ),
                              maxLines: 3,
                              overflow: TextOverflow.ellipsis,
                            ),
                            const SizedBox(height: 8),
                            Text(
                              'Tap to read more →',
                              style: TextStyle(
                                fontSize: 10,
                                color: Colors.green[700],
                                fontWeight: FontWeight.w500,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                  );
                },
              ),
            ),
            
            const SizedBox(height: 24.0),
          ],
        ),
      ),
    );
  }
}