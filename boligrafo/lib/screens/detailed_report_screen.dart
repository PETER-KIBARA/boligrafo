import 'package:flutter/material.dart';

class DetailedReportScreen extends StatefulWidget {
  const DetailedReportScreen({super.key});

  @override
  State<DetailedReportScreen> createState() => _DetailedReportScreenState();
}

class _DetailedReportScreenState extends State<DetailedReportScreen> {
  String _selectedRange = "weekly"; // default filter

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Detailed Reports'),
        actions: [
          PopupMenuButton<String>(
            onSelected: (value) {
              setState(() {
                _selectedRange = value;
              });
              // 🔥 Call your backend here with the selected filter
              // fetchReportData(value);
            },
            itemBuilder: (context) => const [
              PopupMenuItem(value: "weekly", child: Text("Weekly")),
              PopupMenuItem(value: "monthly", child: Text("Monthly")),
            ],
            icon: const Icon(Icons.filter_list),
          ),
        ],
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: ListView(
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
              child: SizedBox(
                height: 200,
                child: Center(
                  child: Text(
                    '[Vitals Chart ($_selectedRange) Placeholder]',
                    style: const TextStyle(color: Colors.green),
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
            // 🔥 Replace with ListView.builder after fetching from API
            const Text("[Fetch vitals from backend here]"),

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
                child: Column(
                  children: const [
                    Text("[Fetch medications from backend here]"),
                  ],
                ),
              ),
            ),

            const SizedBox(height: 24.0),

            // SECTION: Insights (optional backend-driven)
            Text(
              'Insights & Recommendations',
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
            ),
            const SizedBox(height: 8.0),
            const Text(
              '[Optional: show analysis from backend or AI service]',
              style: TextStyle(color: Colors.grey),
            ),
          ],
        ),
      ),
    );
  }
}
