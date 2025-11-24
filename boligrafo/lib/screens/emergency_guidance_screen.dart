import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';

class EmergencyGuidanceScreen extends StatelessWidget {
  const EmergencyGuidanceScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Emergency Guidance'),
        backgroundColor: Colors.red,
      ),
      body: Padding(
        padding: const EdgeInsets.all(20.0),
        child: ListView(
          children: [
            const Icon(Icons.warning_amber_rounded, color: Colors.red, size: 80),
            const SizedBox(height: 16),
            Text(
              'Are you experiencing any of these symptoms?',
              style: Theme.of(context).textTheme.titleLarge?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 16),
            const Text(
              '• Severe headache\n'
              '• Chest pain\n'
              '• Shortness of breath\n'
              '• Blurred vision\n'
              '• Confusion or trouble speaking\n'
              '• Weakness or numbness',
              style: TextStyle(fontSize: 18),
              textAlign: TextAlign.left,
            ),
            const SizedBox(height: 24),
            Card(
              color: Colors.red[50],
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Text(
                  'If you have any of these symptoms, call emergency services immediately or go to the nearest hospital.',
                  style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                        color: Colors.red[900],
                        fontWeight: FontWeight.bold,
                      ),
                  textAlign: TextAlign.center,
                ),
              ),
            ),
            const SizedBox(height: 24),
            Text(
              'If you do not have these symptoms but feel unwell:',
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
            ),
            const SizedBox(height: 8),
            const Text(
              '• Sit or lie down and rest\n'
              '• Take slow, deep breaths\n'
              '• Check your blood pressure if possible\n'
              '• Contact your healthcare provider for advice',
              style: TextStyle(fontSize: 16),
            ),
            const SizedBox(height: 32),
            ElevatedButton.icon(
              icon: const Icon(Icons.phone),
              label: const Text('Call Emergency'),
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.red,
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 14),
                textStyle: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
              ),
              onPressed: () async {
                final Uri phoneUri = Uri(scheme: 'tel', path: '112'); // Replace '112' with your local emergency number
                if (await canLaunchUrl(phoneUri)) {
                  await launchUrl(phoneUri);
                } else {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(
                    content: Text('Could not launch phone dialer'),
                    backgroundColor: Colors.red,
                  ),
    );
  }
},
            ),
          ],
        ),
      ),
    );
  }
}
