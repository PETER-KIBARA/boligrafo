import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:provider/provider.dart';
import 'tips_details.dart';
import 'tips_data.dart';
import 'package:fl_chart/fl_chart.dart';
import 'providers/auth_provider.dart';
import 'providers/vitals_provider.dart';
import 'providers/medication_provider.dart';
import 'medication_service.dart';
import 'dart:async';

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
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
    final authProvider = context.read<AuthProvider>();
    final vitalsProvider = context.read<VitalsProvider>();
    final medicationProvider = context.read<MedicationProvider>();

    if (authProvider.token != null) {
      await Future.wait([
        vitalsProvider.fetchVitals(authProvider.token!),
        medicationProvider.loadMedications(),
      ]);
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
  
  

  List<FlSpot> _spots(List<dynamic> vitals) {
    final List<FlSpot> points = [];
    for (int i = 0; i < vitals.length; i++) {
      final v = vitals[i] as Map<String, dynamic>;
      final y = (v['systolic'] ?? 0).toDouble();
      points.add(FlSpot(i.toDouble(), y));
    }
    return points;
  }

  Widget _buildChart(List<dynamic> vitals) {
    if (vitals.isEmpty) {
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
          maxX: vitals.length > 1 ? (vitals.length - 1).toDouble() : 1,
          minY: 0,
          maxY: vitals.isNotEmpty
              ? (vitals.map((v) => (v['systolic'] ?? 0).toDouble()).reduce(
                      (a, b) => a > b ? a : b) *
                  1.1)
              : 200,
          lineBarsData: [
            LineChartBarData(
              spots: _spots(vitals),
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

 
  

  Future<void> _toggleTaken(MedicationScheduleItem item, bool value) async {
  try {
    final medicationProvider = context.read<MedicationProvider>();
    await medicationProvider.markMedicationTaken(item.id, value);
  } catch (e) {
    debugPrint('Failed to update medication: $e');
    // Optional: show a Snackbar or alert
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text('Failed to update medication. Please try again.')),
    );
  }
}

  @override
  Widget build(BuildContext context) {
    return Consumer3<AuthProvider, VitalsProvider, MedicationProvider>(
      builder: (context, authProvider, vitalsProvider, medicationProvider, child) {
        final isLoading = vitalsProvider.isLoading || medicationProvider.isLoading;
        
        if (isLoading && vitalsProvider.vitals.isEmpty && medicationProvider.medications.isEmpty) {
          return Scaffold(
            body: Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const CircularProgressIndicator(),
                  const SizedBox(height: 18),
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
        // String lastReadingTimestamp = '—';
        
        final vitals = vitalsProvider.vitals;
        if (vitals.isNotEmpty) {
          // Sort vitals by created_at just to be safe
          final sortedVitals = List<Map<String, dynamic>>.from(vitals);
          sortedVitals.sort((a, b) {
            final da = DateTime.tryParse(a['created_at'] ?? '') ?? DateTime(1970);
            final db = DateTime.tryParse(b['created_at'] ?? '') ?? DateTime(1970);
            return da.compareTo(db); // oldest → newest
          });

          final v = sortedVitals.last; // latest reading

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

          // lastReadingTimestamp = v['created_at']?.toString() ?? 'Recent';
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
                '${authProvider.patientName?.isNotEmpty == true ? authProvider.patientName : "Dashboard"}'),
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
                          '${_getGreeting()}, ${authProvider.patientName?.isNotEmpty == true ? authProvider.patientName : "Patient"} ',
                          style: Theme.of(context)
                              .textTheme
                              .titleLarge
                              ?.copyWith(
                                fontWeight: FontWeight.bold,
                                color: Colors.blue[900],
                              ),
                        ),
                        const SizedBox(height: 7.0),
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
                            // children: [
                            //   Text(
                            //     'Last Reading',
                            //     style: TextStyle(
                            //       color: Colors.grey[600],
                            //       fontSize: 12,
                            //     ),
                            //   ),
                            //   const SizedBox(height: 4.0),
                            //   Text(
                            //     lastReadingTimestamp,
                            //     style: const TextStyle(
                            //       fontWeight: FontWeight.w500,
                            //     ),
                            //   ),
                            // ],
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              ),
            ),

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
                    _buildChart(vitals),
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
      },
    );
  }
}