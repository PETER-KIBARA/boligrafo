import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/auth_provider.dart';
import '../providers/vitals_provider.dart';
import '../providers/medication_provider.dart';
import '../api/api_service.dart';
import 'ai_insights_screen.dart';
import 'package:fl_chart/fl_chart.dart';
import 'package:open_filex/open_filex.dart';

class DetailedReportScreen extends StatefulWidget {
  const DetailedReportScreen({super.key});

  @override
  State<DetailedReportScreen> createState() => _DetailedReportScreenState();
}

class _DetailedReportScreenState extends State<DetailedReportScreen> {
  String _selectedRange = "weekly";
  bool _isInit = true;
  List<Map<String, dynamic>> _aiSuggestions = [];
  bool _isLoadingInsights = false;
  bool _isDownloading = false;

  Future<void> _downloadPDF() async {
    final authProvider = context.read<AuthProvider>();
    if (authProvider.token == null) return;

    setState(() => _isDownloading = true);
    try {
      final path = await ApiService.downloadReportPdf(token: authProvider.token!);
      if (path != null) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: const Text("Report downloaded successfully!"),
              action: SnackBarAction(
                label: "Open",
                onPressed: () => OpenFilex.open(path),
              ),
            ),
          );
        }
      } else {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text("Failed to download report.")),
          );
        }
      }
    } catch (e) {
      debugPrint("Error in _downloadPDF: $e");
    } finally {
      if (mounted) setState(() => _isDownloading = false);
    }
  }

  @override
  void didChangeDependencies() {
    if (_isInit) {
      _loadData();
      _isInit = false;
    }
    super.didChangeDependencies();
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
      _fetchAiInsights();
    }
  }

  Future<void> _fetchAiInsights() async {
    final authProvider = context.read<AuthProvider>();
    if (authProvider.token == null || authProvider.userId == null) return;

    setState(() => _isLoadingInsights = true);
    try {
      final response = await ApiService.fetchAISuggestions(
        token: authProvider.token!,
        userId: authProvider.userId!,
      );
      if (mounted && response["error"] != true) {
        setState(() {
          _aiSuggestions = List<Map<String, dynamic>>.from(response['ai_suggestions'] ?? []);
        });
      }
    } catch (e) {
      debugPrint("Error fetching insights in report: $e");
    } finally {
      if (mounted) setState(() => _isLoadingInsights = false);
    }
  }

  List<FlSpot> _getSpots(List<dynamic> vitals) {
    // Reverse to show chronological order if needed
    final sorted = List.from(vitals);
    // Assuming ApiService returns them sorted or we sort here
    final spots = <FlSpot>[];
    for (int i = 0; i < sorted.length; i++) {
      final v = sorted[i];
      spots.add(FlSpot(i.toDouble(), (v['systolic'] ?? 0).toDouble()));
    }
    return spots;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Detailed Reports'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadData,
          ),
          PopupMenuButton<String>(
            onSelected: (value) {
              setState(() {
                _selectedRange = value;
              });
            },
            itemBuilder: (context) => const [
              PopupMenuItem(value: "weekly", child: Text("Weekly")),
              PopupMenuItem(value: "monthly", child: Text("Monthly")),
            ],
            icon: const Icon(Icons.filter_list),
          ),
          _isDownloading 
            ? const Center(child: Padding(
                padding: EdgeInsets.symmetric(horizontal: 16.0),
                child: SizedBox(width: 20, height: 20, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white,)),
              ))
            : IconButton(
                icon: const Icon(Icons.picture_as_pdf),
                onPressed: _downloadPDF,
                tooltip: "Download PDF Report",
              ),
        ],
      ),
      body: Consumer2<VitalsProvider, MedicationProvider>(
        builder: (context, vitalsProvider, medicationProvider, _) {
          final vitals = vitalsProvider.vitals;
          final medications = medicationProvider.medications;

          return RefreshIndicator(
            onRefresh: _loadData,
            child: ListView(
              padding: const EdgeInsets.all(16.0),
              children: [
                // SECTION: Vitals Chart
                Text(
                  'Vitals History ($_selectedRange)',
                  style: Theme.of(context).textTheme.titleLarge?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                ),
                const SizedBox(height: 12.0),
                Card(
                  elevation: 2.0,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12.0),
                  ),
                  child: Container(
                    height: 220,
                    padding: const EdgeInsets.all(16),
                    child: vitals.isEmpty
                        ? const Center(child: Text("No vitals data to display"))
                        : LineChart(
                            LineChartData(
                              gridData: FlGridData(show: false),
                              titlesData: FlTitlesData(
                                bottomTitles: AxisTitles(sideTitles: SideTitles(showTitles: false)),
                                rightTitles: AxisTitles(sideTitles: SideTitles(showTitles: false)),
                                topTitles: AxisTitles(sideTitles: SideTitles(showTitles: false)),
                              ),
                              borderData: FlBorderData(show: false),
                              lineBarsData: [
                                LineChartBarData(
                                  spots: _getSpots(vitals),
                                  isCurved: true,
                                  color: Colors.green,
                                  barWidth: 3,
                                  dotData: FlDotData(show: true),
                                ),
                              ],
                            ),
                          ),
                  ),
                ),
                const SizedBox(height: 24.0),

                // SECTION: Recent Vitals List
                Text(
                  'Recent Vitals',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                ),
                const SizedBox(height: 8.0),
                if (vitals.isEmpty)
                  const Text("No vitals recorded yet.")
                else
                  ...vitals.reversed.take(5).map((v) => ListTile(
                        leading: const Icon(Icons.monitor_heart, color: Colors.redAccent),
                        title: Text("${v['systolic']}/${v['diastolic']} mmHg"),
                        subtitle: Text(v['created_at'] ?? ""),
                        trailing: Text("HR: ${v['heartrate'] ?? '--'}"),
                      )),

                const SizedBox(height: 24.0),

                // SECTION: Medications
                Text(
                  'Medications Assigned',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                ),
                const SizedBox(height: 8.0),
                Card(
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12.0),
                  ),
                  elevation: 2,
                  child: Padding(
                    padding: const EdgeInsets.all(12.0),
                    child: medications.isEmpty
                        ? const Text("No medications assigned.")
                        : Column(
                            children: medications
                                .map((m) => ListTile(
                                      leading: const Icon(Icons.medication, color: Colors.blue),
                                      title: Text(m.name),
                                      subtitle: Text("${m.dosage} - ${m.frequency}"),
                                    ))
                                .toList(),
                          ),
                  ),
                ),

                const SizedBox(height: 24.0),

                // SECTION: Insights
                Text(
                  'Insights & Recommendations',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                ),
                const SizedBox(height: 8.0),
                if (_isLoadingInsights)
                  const Center(child: CircularProgressIndicator())
                else if (_aiSuggestions.isEmpty)
                  const Text(
                    'No personalized insights available yet. Keep logging your data.',
                    style: TextStyle(color: Colors.grey),
                  )
                else
                  ..._aiSuggestions.take(3).map((s) => SuggestionCard(suggestion: s)),
                
                if (_aiSuggestions.isNotEmpty)
                  TextButton(
                    onPressed: () {
                      Navigator.push(
                        context,
                        MaterialPageRoute(builder: (context) => const AIInsightsScreen()),
                      );
                    },
                    child: const Text("View All Insights →"),
                  ),
                const SizedBox(height: 32),
              ],
            ),
          );
        },
      ),
    );
  }
}
