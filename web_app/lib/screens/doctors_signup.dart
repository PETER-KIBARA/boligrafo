import 'package:flutter/material.dart';

class DoctorsSignupScreen extends StatefulWidget {
  const DoctorsSignupScreen({super.key});

  @override
  State<DoctorsSignupScreen> createState() => _DoctorsSignupScreenState();
}

class _DoctorsSignupScreenState extends State<DoctorsSignupScreen> {
  final _formKey = GlobalKey<FormState>();

  // Form fields
  String fullName = '';
  String email = '';
  String phone = '';
  String nationalId = '';
  String employeeId = '';
  String specialty = '';
  String title = '';
  String password = '';
  String confirmPassword = '';

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.blue[50],
      appBar: AppBar(
        title: const Text("Doctor Signup"),
        centerTitle: true,
        backgroundColor: Colors.blue,
        elevation: 0,
      ),
      body: Center(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24),
          child: ConstrainedBox(
            constraints: const BoxConstraints(
              maxWidth: 600,
            ),
            child: Card(
              color: Colors.white,
              elevation: 8,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(20),
              ),
              child: Padding(
                padding: const EdgeInsets.all(24),
                child: Form(
                  key: _formKey,
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      const Text(
                        "Create Doctor Account",
                        style: TextStyle(
                          fontSize: 24,
                          fontWeight: FontWeight.bold,
                          color: Colors.blue,
                        ),
                      ),
                      const SizedBox(height: 24),

                      _buildTextField("Full Legal Name", Icons.person,
                          onSaved: (v) => fullName = v ?? ''),

                      _gap(),
                      _buildTextField("Primary Email Address", Icons.email,
                          keyboardType: TextInputType.emailAddress,
                          validator: (v) {
                            if (v == null || v.isEmpty) return "Enter your email";
                            if (!RegExp(r'^[^@]+@[^@]+\.[^@]+').hasMatch(v)) {
                              return "Enter a valid email";
                            }
                            return null;
                          },
                          onSaved: (v) => email = v ?? ''),

                      _gap(),
                      _buildTextField("Mobile Phone Number", Icons.phone,
                          keyboardType: TextInputType.phone,
                          onSaved: (v) => phone = v ?? ''),

                      _gap(),
                      _buildTextField("National ID / Passport Number",
                          Icons.credit_card,
                          onSaved: (v) => nationalId = v ?? ''),

                      _gap(),
                      _buildTextField("Employee ID / Staff Number", Icons.badge,
                          onSaved: (v) => employeeId = v ?? ''),

                      _gap(),
                      _buildTextField("Specialty", Icons.medical_services,
                          onSaved: (v) => specialty = v ?? ''),

                      _gap(),
                      _buildTextField("Official Title", Icons.work,
                          onSaved: (v) => title = v ?? ''),

                      _gap(),
                      _buildTextField("Password", Icons.lock,
                          isPassword: true,
                          validator: (v) => v == null || v.length < 6
                              ? "Password must be at least 6 characters"
                              : null,
                          onSaved: (v) => password = v ?? ''),

                      _gap(),
                      _buildTextField("Confirm Password", Icons.lock_outline,
                          isPassword: true,
                          validator: (v) =>
                              v != password ? "Passwords do not match" : null,
                          onSaved: (v) => confirmPassword = v ?? ''),

                      const SizedBox(height: 24),

                      SizedBox(
                        width: double.infinity,
                        child: ElevatedButton(
                          style: ElevatedButton.styleFrom(
                            padding: const EdgeInsets.symmetric(vertical: 16),
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(12),
                            ),
                            backgroundColor: Colors.blue,
                          ),
                          child: const Text(
                            "Sign Up",
                            style:
                                TextStyle(fontSize: 18, color: Colors.white),
                          ),
                          onPressed: () {
                            if (_formKey.currentState?.validate() ?? false) {
                              _formKey.currentState?.save();
                              ScaffoldMessenger.of(context).showSnackBar(
                                const SnackBar(
                                    content: Text("Signup successful!")),
                              );
                            }
                          },
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildTextField(
    String label,
    IconData icon, {
    bool isPassword = false,
    TextInputType keyboardType = TextInputType.text,
    String? Function(String?)? validator,
    void Function(String?)? onSaved,
  }) {
    return TextFormField(
      decoration: InputDecoration(
        labelText: label,
        prefixIcon: Icon(icon, color: Colors.blue),
        border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
      ),
      obscureText: isPassword,
      keyboardType: keyboardType,
      validator: validator ??
          (value) => value == null || value.isEmpty ? "Enter $label" : null,
      onSaved: onSaved,
    );
  }

  Widget _gap() => const SizedBox(height: 16);
}
