import 'package:flutter/material.dart';

class LogVitalsScreen extends StatefulWidget {
  const LogVitalsScreen({super.key});

  @override
  _LogVitalsScreenState createState() => _LogVitalsScreenState();
}

class _LogVitalsScreenState extends State<LogVitalsScreen> {
  final _formKey = GlobalKey<FormState>();
  final TextEditingController _systolicController = TextEditingController();
  final TextEditingController _diastolicController = TextEditingController();
  final TextEditingController _symptomsController = TextEditingController();

  @override
  void dispose() {
    _systolicController.dispose();
    _diastolicController.dispose();
    _symptomsController.dispose();
    super.dispose();
  }

  void _saveReading() {
    if (_formKey.currentState!.validate()) {
      // Process data
      final systolic = _systolicController.text;
      final diastolic = _diastolicController.text;
      final symptoms = _symptomsController.text;

      // TODO: Save the data (e.g., to local storage or send to API)
      print('Systolic: $systolic, Diastolic: $diastolic, Symptoms: $symptoms');

      // Show a confirmation message
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Vitals saved successfully!')),
      );

      // Optionally navigate back
      Navigator.pop(context);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Log Vitals'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Form(
          key: _formKey,
          child: ListView(
            children: [
              TextFormField(
                controller: _systolicController,
                keyboardType: TextInputType.number,
                decoration: const InputDecoration(
                  labelText: 'Systolic Blood Pressure (mmHg)',
                  border: OutlineInputBorder(),
                ),
                validator: (value) {
                  if (value == null || value.isEmpty) {
                    return 'Please enter systolic reading';
                  }
                  if (int.tryParse(value) == null) {
                    return 'Please enter a valid number';
                  }
                  return null;
                },
              ),
              const SizedBox(height: 16.0),
              TextFormField(
                controller: _diastolicController,
                keyboardType: TextInputType.number,
                decoration: const InputDecoration(
                  labelText: 'Diastolic Blood Pressure (mmHg)',
                  border: OutlineInputBorder(),
                ),
                validator: (value) {
                  if (value == null || value.isEmpty) {
                    return 'Please enter diastolic reading';
                  }
                   if (int.tryParse(value) == null) {
                    return 'Please enter a valid number';
                  }
                  return null;
                },
              ),
              const SizedBox(height: 16.0),
              TextFormField(
                controller: _symptomsController,
                keyboardType: TextInputType.text,
                decoration: const InputDecoration(
                  labelText: 'Symptoms (Optional)',
                  border: OutlineInputBorder(),
                  alignLabelWithHint: true,
                ),
                maxLines: 3,
              ),
              const SizedBox(height: 24.0),
              ElevatedButton(
                onPressed: _saveReading,
                style: ElevatedButton.styleFrom(
                   padding: const EdgeInsets.symmetric(vertical: 12.0),
                   textStyle: Theme.of(context).textTheme.titleMedium,
                ),
                child: const Text('Save Reading'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
