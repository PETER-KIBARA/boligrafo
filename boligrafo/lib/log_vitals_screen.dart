import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../Api/api_service.dart';


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

  Future<void> _saveReading() async {
  if (_formKey.currentState!.validate()) {
    final systolic = int.parse(_systolicController.text);
    final diastolic = int.parse(_diastolicController.text);
    final symptoms = _symptomsController.text;

    final prefs = await SharedPreferences.getInstance();
    final token = prefs.getString("doctorToken") ?? ""; // or patient token

    final result = await ApiService.saveVital(
      token: token,
      systolic: systolic,
      diastolic: diastolic,
      symptoms: symptoms,
    );

    if (result["error"] == true) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text("Error: ${result['message']}")),
      );
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text("Vitals saved successfully!")),
      );
      Navigator.pop(context);
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
