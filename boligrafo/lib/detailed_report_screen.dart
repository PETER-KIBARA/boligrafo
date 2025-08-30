import 'package:flutter/material.dart';

class DetailedReportScreen extends StatelessWidget {
  const DetailedReportScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Detailed Reports'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: ListView(
          children: [
            Text(
              'Blood Pressure History',
              style: Theme.of(context).textTheme.titleLarge?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
            ),
            const SizedBox(height: 16.0),
            // Placeholder for a chart or list of readings
            Card(
              elevation: 2.0,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12.0),
              ),
              child: Container(
                height: 200,
                alignment: Alignment.center,
                child: const Text(
                  '[Blood Pressure Chart Placeholder]',
                  style: TextStyle(color: Colors.green),
                ),
              ),
            ),
            const SizedBox(height: 24.0),
            Text(
              'Recent Readings',
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
            ),
            const SizedBox(height: 8.0),
            // Example readings list
            ...[
              {'date': 'July 28, 2025', 'bp': '120/80 mmHg', 'status': 'Normal'},
              {'date': 'July 27, 2025', 'bp': '130/85 mmHg', 'status': 'Elevated'},
              {'date': 'July 26, 2025', 'bp': '140/90 mmHg', 'status': 'Critical'},
            ].map((reading) => ListTile(
                  leading: const Icon(Icons.favorite, color: Color.fromARGB(255, 199, 226, 46)),
                  title: Text('${reading['bp']} (${reading['status']})'),
                  subtitle: Text(reading['date']!),
                )),
            const SizedBox(height: 24.0),
            Text(
              'Insights & Recommendations',
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
            ),
            const SizedBox(height: 8.0),
            const Text(
              'Your blood pressure has been mostly within the normal range. Keep up with your medication and healthy lifestyle habits!',
            ),
          ],
        ),
      ),
    );
  }
}