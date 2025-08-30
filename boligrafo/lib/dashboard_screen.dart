import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'log_vitals_screen.dart'; 
import 'detailed_report_screen.dart';
import 'emergency_guidance_screen.dart';
import 'tips_details.dart';
import 'tips_data.dart';

class DashboardScreen extends StatelessWidget {
  const DashboardScreen({super.key});


  @override
  Widget build(BuildContext context) {
    final DateTime now = DateTime.now();
    final String formattedDate = DateFormat('EEEE, MMMM d').format(now);
    final String formattedTime = DateFormat('h:mm a').format(now);

  
    const String latestBpReading = '120/80 mmHg';
    const String bpStatus = 'Normal';
    const String lastReadingTimestamp = '10:30 AM, Today';
    final List<Map<String, String>> medications = [
      {'name': 'Lisinopril', 'time': '8:00 AM'},
      {'name': 'Amlodipine', 'time': '6:00 PM'},
    ];
    Text(
  'Lifestyle Tips',
  style: Theme.of(context).textTheme.titleLarge?.copyWith(
        fontWeight: FontWeight.bold,
      ),
);

const SizedBox(height: 16.0);

SizedBox(
  height: 160.0,
  child: ListView.builder(
    scrollDirection: Axis.horizontal,
    itemCount: lifestyleTips.length, // from tips_data.dart
    itemBuilder: (context, index) {
      // ✅ tip is defined here
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
);


    Color statusColor = const Color(0xFF4CAF50);
    if (bpStatus == 'Elevated') {
      statusColor = Colors.orange;
    } else if (bpStatus == 'Critical') {
      statusColor = Colors.red;
    }

    return Scaffold(
      appBar: AppBar(
        title: const Text('Hypertension Management'),
        elevation: 0,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            
            Text(
              'Good morning, Peter!',
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
            const SizedBox(height: 24.0),

            
            Center(
              child: ElevatedButton.icon(
                onPressed: () {
                  Navigator.push(
                    context,
                    MaterialPageRoute(builder: (context) => const LogVitalsScreen()),
                  );
                },
                icon: const Icon(Icons.add_circle_outline),
                label: const Text('Log Blood Pressure or Symptoms'),
                style: ElevatedButton.styleFrom(
                  padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
                  textStyle: Theme.of(context).textTheme.titleMedium,
                ),
              ),
            ),
            const SizedBox(height: 24.0),

           
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
              itemCount: medications.length,
              itemBuilder: (context, index) {
                final medication = medications[index];
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
                                medication['name']!,
                                style: Theme.of(context).textTheme.titleMedium,
                              ),
                              const SizedBox(height: 4.0),
                              Text(
                                medication['time']!,
                                style: Theme.of(context).textTheme.titleSmall?.copyWith(
                                      color: Colors.grey[600],
                                    ),
                              ),
                            ],
                          ),
                        ),
                        Checkbox(
                          value: false, 
                          onChanged: (bool? value) {
                          
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
              child: Container(
                height: 200, 
                alignment: Alignment.center,
                child: const Text(
                  '[Blood Pressure Trends Chart Placeholder]',
                  style: TextStyle(color: Color.fromARGB(255, 15, 150, 2)),
                ),
              ),
            ),
            const SizedBox(height: 16.0),
            Align(
  alignment: Alignment.centerRight,
  child: TextButton(
    onPressed: () {
      Navigator.push(
        context,
        MaterialPageRoute(builder: (context) => const DetailedReportScreen()),
      );
    },
    child: const Text('View Detailed Reports'),
  ),
),
                       const SizedBox(height: 24.0),
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
          // ✅ Navigate to detail screen when tapped
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
                  'Tip #${tip.id}', // ✅ use id instead of raw string
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                        fontWeight: FontWeight.bold,
                        color: Colors.black54,
                      ),
                ),
                const SizedBox(height: 8),
                Text(
                  tip.title, // ✅ use title instead of raw string
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
const SizedBox(height: 24.0),

  
            Center(
  child: ElevatedButton.icon(
    onPressed: () {
      Navigator.push(
        context,
        MaterialPageRoute(builder: (context) => const EmergencyGuidanceScreen()),
      );
    },
    icon: const Icon(Icons.warning_amber_outlined),
    label: const Text('Feeling Unwell? Get Guidance'),
    style: ElevatedButton.styleFrom(
      backgroundColor: Colors.red, 
      foregroundColor: Colors.white,
      padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
      textStyle: Theme.of(context).textTheme.titleMedium,
    ),
  ),
),
             const SizedBox(height: 24.0),
          ],
        ),
      ),
    );            
  }
}
