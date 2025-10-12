import 'package:flutter/material.dart';
import 'package:myapp/main_screen.dart';
import 'package:provider/provider.dart';
import 'providers/auth_provider.dart';
import 'providers/vitals_provider.dart';

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
      final authProvider = context.read<AuthProvider>();
      final vitalsProvider = context.read<VitalsProvider>();

      final systolic = int.parse(_systolicController.text);
      final diastolic = int.parse(_diastolicController.text);
      final symptoms = _symptomsController.text.trim();
      final heartRate = _heartRateController.text.isEmpty
          ? null
          : int.parse(_heartRateController.text);
      final diet =
          _dietController.text.isEmpty ? null : _dietController.text.trim();
      final exercise = _exerciseController.text.isEmpty
          ? null
          : _exerciseController.text.trim();

      final result = await vitalsProvider.saveVital(
        token: authProvider.token!,
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
          SnackBar(
            content: Text(result["message"] ?? "Failed to save vitals"),
            backgroundColor: Colors.red,
            behavior: SnackBarBehavior.floating,
          ),
        );
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: const Text("Vitals saved successfully!"),
            backgroundColor: Colors.green,
            behavior: SnackBarBehavior.floating,
          ),
        );

        // Clear form after successful save
        _systolicController.clear();
        _diastolicController.clear();
        _heartRateController.clear();
        _symptomsController.clear();
        _dietController.clear();
        _exerciseController.clear();

        Navigator.pushReplacement(
          context,
          MaterialPageRoute(builder: (context) => const MainScreen()),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey[50],
      appBar: AppBar(
        title: const Text(
          'Log Vitals',
          style: TextStyle(
            fontWeight: FontWeight.w600,
            color: Colors.white,
          ),
        ),
        centerTitle: true,
        backgroundColor: Colors.blue[700],
        elevation: 0,
        iconTheme: const IconThemeData(color: Colors.white),
      ),
      body: Padding(
        padding: const EdgeInsets.all(20.0),
        child: Form(
          key: _formKey,
          child: Column(
            children: [
              // Header Card
              Card(
                elevation: 2,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: Row(
                    children: [
                      Icon(
                        Icons.favorite,
                        color: Colors.red[400],
                        size: 24,
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Text(
                          'Track your health vitals regularly for better monitoring',
                          style: TextStyle(
                            color: Colors.grey[700],
                            fontSize: 14,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 24),

              Expanded(
                child: ListView(
                  physics: const BouncingScrollPhysics(),
                  children: [
                    // Blood Pressure Section
                    _buildSectionHeader('Blood Pressure'),
                    const SizedBox(height: 16),
                    Row(
                      children: [
                        Expanded(
                          child: _buildTextField(
                            controller: _systolicController,
                            label: 'Systolic (mmHg)',
                            icon: Icons.monitor_heart,
                            isRequired: true,
                            keyboardType: TextInputType.number,
                          ),
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: _buildTextField(
                            controller: _diastolicController,
                            label: 'Diastolic (mmHg)',
                            icon: Icons.monitor_heart,
                            isRequired: true,
                            keyboardType: TextInputType.number,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 20),

                    // Heart Rate Section
                    _buildSectionHeader('Heart Rate'),
                    const SizedBox(height: 16),
                    _buildTextField(
                      controller: _heartRateController,
                      label: 'Heart Rate (bpm)',
                      icon: Icons.favorite_border,
                      isRequired: false,
                      keyboardType: TextInputType.number,
                    ),
                    const SizedBox(height: 20),

                    // Symptoms Section
                    _buildSectionHeader('Symptoms & Lifestyle'),
                    const SizedBox(height: 16),
                    _buildTextField(
                      controller: _symptomsController,
                      label: 'Symptoms',
                      icon: Icons.health_and_safety,
                      isRequired: false,
                      maxLines: 3,
                    ),
                    const SizedBox(height: 16),
                    _buildTextField(
                      controller: _dietController,
                      label: 'Diet Notes',
                      icon: Icons.restaurant,
                      isRequired: false,
                      maxLines: 2,
                    ),
                    const SizedBox(height: 16),
                    _buildTextField(
                      controller: _exerciseController,
                      label: 'Exercise Activity',
                      icon: Icons.directions_run,
                      isRequired: false,
                      maxLines: 2,
                    ),
                    const SizedBox(height: 32),

                    // Save Button
                    _buildSaveButton(),
                    const SizedBox(height: 20),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildSectionHeader(String title) {
    return Text(
      title,
      style: TextStyle(
        fontSize: 18,
        fontWeight: FontWeight.w600,
        color: Colors.blue[800],
      ),
    );
  }

  Widget _buildTextField({
    required TextEditingController controller,
    required String label,
    required IconData icon,
    required bool isRequired,
    TextInputType keyboardType = TextInputType.text,
    int maxLines = 1,
  }) {
    return TextFormField(
      controller: controller,
      keyboardType: keyboardType,
      maxLines: maxLines,
      decoration: InputDecoration(
        labelText: label + (isRequired ? ' *' : ''),
        labelStyle: TextStyle(color: Colors.grey[600]),
        prefixIcon: Icon(icon, color: Colors.blue[400]),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: BorderSide(color: Colors.grey[300]!),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: BorderSide(color: Colors.grey[300]!),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: BorderSide(color: Colors.blue[400]!, width: 2),
        ),
        filled: true,
        fillColor: Colors.white,
      ),
      validator: (value) {
        if (isRequired && (value == null || value.isEmpty)) {
          return 'This field is required';
        }
        if (keyboardType == TextInputType.number &&
            value != null &&
            value.isNotEmpty &&
            int.tryParse(value) == null) {
          return 'Please enter a valid number';
        }
        return null;
      },
    );
  }

  Widget _buildSaveButton() {
    return Consumer<VitalsProvider>(
      builder: (context, vitalsProvider, child) {
        return SizedBox(
          width: double.infinity,
          height: 54,
          child: ElevatedButton(
            onPressed: vitalsProvider.isLoading ? null : _saveReading,
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.blue[700],
              foregroundColor: Colors.white,
              elevation: 2,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12),
              ),
              padding: const EdgeInsets.symmetric(vertical: 16),
            ),
            child: vitalsProvider.isLoading
                ? SizedBox(
                    height: 20,
                    width: 20,
                    child: CircularProgressIndicator(
                      strokeWidth: 2,
                      valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                    ),
                  )
                : const Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(Icons.save, size: 20),
                      SizedBox(width: 8),
                      Text(
                        'Save Vitals',
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ],
                  ),
          ),
        );
      },
    );
  }
}