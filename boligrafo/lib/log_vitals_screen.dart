import 'package:flutter/material.dart';
import 'package:myapp/main_screen.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../Api/api_service.dart';

class LogVitalsScreen extends StatefulWidget {
  const LogVitalsScreen({super.key});

  @override
  State<LogVitalsScreen> createState() => _LogVitalsScreenState();
}

class _LogVitalsScreenState extends State<LogVitalsScreen> {
  final _formKey = GlobalKey<FormState>();

  final TextEditingController _systolicController = TextEditingController();
  final TextEditingController _diastolicController = TextEditingController();
  final TextEditingController _heartRateController = TextEditingController();
  final TextEditingController _symptomsController = TextEditingController();
  final TextEditingController _dietController = TextEditingController();
  final TextEditingController _exerciseController = TextEditingController();

  @override
  void dispose() {
    _systolicController.dispose();
    _diastolicController.dispose();
    _heartRateController.dispose();
    _symptomsController.dispose();
    _dietController.dispose();
    _exerciseController.dispose();
    super.dispose();
  }
Future<void> _saveReading() async {
  if (_formKey.currentState!.validate()) {
    final systolic = int.parse(_systolicController.text);
    final diastolic = int.parse(_diastolicController.text);
    final symptoms = _symptomsController.text.trim();
    final heartRate = _heartRateController.text.isEmpty
        ? null
        : int.parse(_heartRateController.text);
    final diet =
        _dietController.text.isEmpty ? null : _dietController.text.trim();
    final exercise =
        _exerciseController.text.isEmpty ? null : _exerciseController.text.trim();

    final prefs = await SharedPreferences.getInstance();
    final token = prefs.getString("patientToken") ?? "";

    final result = await ApiService.saveVital(
      token: token,
      systolic: systolic,
      diastolic: diastolic,
      heartRate: heartRate,
      symptoms: symptoms,
      diet: diet,
      exercise: exercise,
    );

    if (!mounted) return;

    if (result.containsKey("error")) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(result["message"] ?? "Failed to save vitals")),
      );
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text("Vitals saved successfully!")),
      );

      // 🚀 Replace pop with navigation to dashboard
      Navigator.pushReplacement(
        context,
        MaterialPageRoute(builder: (context) => const MainScreen() ),
      );
    }
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
                controller: _heartRateController,
                keyboardType: TextInputType.number,
                decoration: const InputDecoration(
                  labelText: 'Heart Rate (bpm) - Optional',
                  border: OutlineInputBorder(),
                ),
                validator: (value) {
                  if (value != null &&
                      value.isNotEmpty &&
                      int.tryParse(value) == null) {
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
              const SizedBox(height: 16.0),
              TextFormField(
                controller: _dietController,
                keyboardType: TextInputType.text,
                decoration: const InputDecoration(
                  labelText: 'Diet (Optional)',
                  border: OutlineInputBorder(),
                  alignLabelWithHint: true,
                ),
                maxLines: 2,
              ),
              const SizedBox(height: 16.0),
              TextFormField(
                controller: _exerciseController,
                keyboardType: TextInputType.text,
                decoration: const InputDecoration(
                  labelText: 'Exercise (Optional)',
                  border: OutlineInputBorder(),
                  alignLabelWithHint: true,
                ),
                maxLines: 2,
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
