import 'package:flutter/material.dart';
import 'dart:math' as math;
import '../Api/api_service.dart';

class SignupScreen extends StatefulWidget {
  const SignupScreen({super.key});

  @override
  State<SignupScreen> createState() => _SignupScreenState();
}

class _SignupScreenState extends State<SignupScreen> with TickerProviderStateMixin {
  final _formKey = GlobalKey<FormState>();
  final _nameController = TextEditingController();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  final _confirmPasswordController = TextEditingController();
  final _phoneController = TextEditingController();
  final _addressController = TextEditingController();
  final TextEditingController _dobController = TextEditingController();
  final TextEditingController _genderController = TextEditingController();
  final _emergencyNameController = TextEditingController();
  final _emergencyPhoneController = TextEditingController();
  final _emergencyRelationController = TextEditingController();
  
  bool _obscurePassword = true;
  bool _obscureConfirmPassword = true;
  bool _isLoading = false;
  DateTime? _selectedDate;
  String? _selectedGender;
  int? _calculatedAge;

  final List<String> _genders = ['Male', 'Female'];

  // Animation controllers
  late AnimationController _particleController;
  late AnimationController _gradientController;
  late Animation<double> _particleAnimation;
  late Animation<double> _gradientAnimation;

final ApiService _apiService = ApiService();
Future<void> _submitForm() async {
  if (_formKey.currentState!.validate()) {
    setState(() => _isLoading = true);

    // Call your API
    final response = await _apiService.signup(
      name: _nameController.text.trim(),
      email: _emailController.text.trim(),
      password: _passwordController.text.trim(),
      confirmPassword: _confirmPasswordController.text.trim(),
      phone: _phoneController.text.trim(),
      address: _addressController.text.trim(),
      dob: _dobController.text.trim(),   // Format: "YYYY-MM-DD"
      gender: _genderController.text.trim(),
      emergencyName: _emergencyNameController.text.trim(),
      emergencyPhone: _emergencyPhoneController.text.trim(),
      emergencyRelation: _emergencyRelationController.text.trim(),
    );

    setState(() => _isLoading = false);

    if (response["success"]) {
      
      ScaffoldMessenger.of(context).showSnackBar(
        
        const SnackBar(content: Text("Account created successfully!")),
      );
      Navigator.of(context).pop(); // Go back to login or previous screen
    } else {
      // ❌ Show error
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(response["message"] ?? "Signup failed")),
      );
    }
  }
}

   
  @override
  void initState() {
    super.initState();
    
    
    _particleController = AnimationController(
      duration: const Duration(seconds: 20),
      vsync: this,
    )..repeat();
    
    _gradientController = AnimationController(
      duration: const Duration(seconds: 8),
      vsync: this,
    )..repeat(reverse: true);

    _particleAnimation = Tween<double>(
      begin: 0.0,
      end: 1.0,
    ).animate(_particleController);
    
    _gradientAnimation = Tween<double>(
      begin: 0.0,
      end: 1.0,
    ).animate(_gradientController);
  }

  @override
  void dispose() {
    _nameController.dispose();
    _emailController.dispose();
    _passwordController.dispose();
    _confirmPasswordController.dispose();
    _phoneController.dispose();
    _addressController.dispose();
    _emergencyNameController.dispose();
    _emergencyPhoneController.dispose();
    _emergencyRelationController.dispose();
    
    // Dispose animation controllers
    _particleController.dispose();
    _gradientController.dispose();
    
    super.dispose();
  }

  Future<void> _selectDate(BuildContext context) async {
    final DateTime? picked = await showDatePicker(
      context: context,
      initialDate: DateTime.now(),
      firstDate: DateTime(1900),
      lastDate: DateTime.now(),
    );
    if (picked != null && picked != _selectedDate) {
      setState(() {
        _selectedDate = picked;
        _calculatedAge = DateTime.now().year - picked.year;
      });
    }
  }

  

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Create Account'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => Navigator.of(context).pop(),
        ),
        backgroundColor: Colors.transparent,
        elevation: 0,
      ),
      extendBodyBehindAppBar: true,
      body: Stack(
        children: [
          // Animated background
          _buildAnimatedBackground(),
          
          // Content
          SafeArea(
            child: SingleChildScrollView(
              padding: const EdgeInsets.all(20.0),
              child: Center(
                child: ConstrainedBox(
                  constraints: const BoxConstraints(maxWidth: 500),
                  child: Column(
                    children: [
                      const SizedBox(height: 60), // Space for transparent app bar
                      _buildHeader(),
                      const SizedBox(height: 24),
                      _buildSignupForm(),
                    ],
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildHeader() {
    return Column(
      children: [
        Container(
          width: 70,
          height: 70,
          decoration: BoxDecoration(
            color: Colors.blue.shade100,
            shape: BoxShape.circle,
          ),
          child: const Icon(
            Icons.person_add,
            size: 35,
            color: Colors.blue,
          ),
        ),
        const SizedBox(height: 16),
        Text(
          'Create Account',
          style: TextStyle(
            fontSize: 22,
            fontWeight: FontWeight.bold,
            color: Colors.blue.shade800,
          ),
        ),
        const SizedBox(height: 8),
        Text(
          'Fill in your details to get started',
          style: TextStyle(
            fontSize: 14,
            color: Colors.grey.shade600,
          ),
          textAlign: TextAlign.center,
        ),
      ],
    );
  }

  Widget _buildSignupForm() {
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.9),
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.1),
            blurRadius: 20,
            offset: const Offset(0, 10),
          ),
        ],
      ),
      child: Form(
        key: _formKey,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildSectionHeader('Personal Information'),
            const SizedBox(height: 16),
          TextFormField(
            controller: _nameController,
            decoration: InputDecoration(
              labelText: 'Full Name',
              prefixIcon: const Icon(Icons.person_outline, size: 20),
              border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
              contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
            ),
            validator: (value) => value == null || value.isEmpty ? 'Please enter your name' : null,
          ),
          const SizedBox(height: 16),
          Row(
            children: [
              Expanded(
                child: InkWell(
                  onTap: () => _selectDate(context),
                  child: InputDecorator(
                    decoration: InputDecoration(
                      labelText: 'Date of Birth',
                      prefixIcon: const Icon(Icons.calendar_today, size: 20),
                      border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
                      contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
                    ),
                    child: Text(
                      _selectedDate != null
                          ? '${_selectedDate!.year}/${_selectedDate!.month}/${_selectedDate!.day}'
                          : 'Select date',
                      style: TextStyle(
                        color: _selectedDate != null ? Colors.black : Colors.grey.shade500,
                      ),
                    ),
                  ),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: TextFormField(
                  readOnly: true,
                  decoration: InputDecoration(
                    labelText: 'Age',
                    prefixIcon: const Icon(Icons.cake, size: 20),
                    border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
                    contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
                  ),
                  controller: TextEditingController(
                    text: _calculatedAge != null ? '$_calculatedAge years' : '',
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          DropdownButtonFormField<String>(
            value: _selectedGender,
            decoration: InputDecoration(
              labelText: 'Gender',
              prefixIcon: const Icon(Icons.transgender, size: 20),
              border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
              contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 14),
            ),
            items: _genders.map((gender) => DropdownMenuItem(value: gender, child: Text(gender, style: const TextStyle(fontSize: 14)))).toList(),
            onChanged: (value) => setState(() => _selectedGender = value),
            validator: (value) => value == null || value.isEmpty ? 'Please select gender' : null,
          ),
          const SizedBox(height: 24),
          _buildSectionHeader('Contact Information'),
          const SizedBox(height: 16),
          TextFormField(
            controller: _emailController,
            keyboardType: TextInputType.emailAddress,
            decoration: InputDecoration(
              labelText: 'Email',
              prefixIcon: const Icon(Icons.email_outlined, size: 20),
              border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
              contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
            ),
            validator: (value) {
              if (value == null || value.isEmpty) return 'Please enter your email';
              if (!RegExp(r'^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$').hasMatch(value)) return 'Please enter a valid email';
              return null;
            },
          ),
          const SizedBox(height: 16),
          TextFormField(
            controller: _phoneController,
            keyboardType: TextInputType.phone,
            decoration: InputDecoration(
              labelText: 'Phone Number',
              prefixIcon: const Icon(Icons.phone, size: 20),
              border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
              contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
            ),
            validator: (value) {
              if (value == null || value.isEmpty) return 'Please enter phone number';
              if (value.length < 10) return 'Please enter valid phone number';
              return null;
            },
          ),
          const SizedBox(height: 16),
          TextFormField(
            controller: _addressController,
            maxLines: 2,
            decoration: InputDecoration(
              labelText: 'Address',
              prefixIcon: const Icon(Icons.home, size: 20),
              border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
              contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
            ),
            validator: (value) => value == null || value.isEmpty ? 'Please enter your address' : null,
          ),
          const SizedBox(height: 24),
          _buildSectionHeader('Emergency Contact'),
          const SizedBox(height: 16),
          TextFormField(
            controller: _emergencyNameController,
            decoration: InputDecoration(
              labelText: 'Emergency Contact Name',
              prefixIcon: const Icon(Icons.emergency, size: 20),
              border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
              contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
            ),
            validator: (value) => value == null || value.isEmpty ? 'Please enter emergency contact name' : null,
          ),
          const SizedBox(height: 16),
          TextFormField(
            controller: _emergencyPhoneController,
            keyboardType: TextInputType.phone,
            decoration: InputDecoration(
              labelText: 'Emergency Contact Phone',
              prefixIcon: const Icon(Icons.phone_android, size: 20),
              border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
              contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
            ),
            validator: (value) {
              if (value == null || value.isEmpty) return 'Please enter emergency phone number';
              if (value.length < 10) return 'Please enter valid phone number';
              return null;
            },
          ),
          const SizedBox(height: 16),
          TextFormField(
            controller: _emergencyRelationController,
            decoration: InputDecoration(
              labelText: 'Relationship',
              prefixIcon: const Icon(Icons.people, size: 20),
              border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
              contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
            ),
            validator: (value) => value == null || value.isEmpty ? 'Please enter relationship' : null,
          ),
          const SizedBox(height: 24),
          _buildSectionHeader('Security'),
          const SizedBox(height: 16),
          TextFormField(
            controller: _passwordController,
            obscureText: _obscurePassword,
            decoration: InputDecoration(
              labelText: 'Password',
              prefixIcon: const Icon(Icons.lock_outline, size: 20),
              suffixIcon: IconButton(
                icon: Icon(_obscurePassword ? Icons.visibility_off : Icons.visibility, size: 20),
                onPressed: () => setState(() => _obscurePassword = !_obscurePassword),
              ),
              border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
              contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
            ),
            validator: (value) {
              if (value == null || value.isEmpty) return 'Please enter your password';
              if (value.length < 6) return 'Password must be at least 6 characters';
              return null;
            },
          ),
          const SizedBox(height: 16),
          TextFormField(
            controller: _confirmPasswordController,
            obscureText: _obscureConfirmPassword,
            decoration: InputDecoration(
              labelText: 'Confirm Password',
              prefixIcon: const Icon(Icons.lock_outline, size: 20),
              suffixIcon: IconButton(
                icon: Icon(_obscureConfirmPassword ? Icons.visibility_off : Icons.visibility, size: 20),
                onPressed: () => setState(() => _obscureConfirmPassword = !_obscureConfirmPassword),
              ),
              border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
              contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
            ),
            validator: (value) {
              if (value == null || value.isEmpty) return 'Please confirm your password';
              if (value != _passwordController.text) return 'Passwords do not match';
              return null;
            },
          ),
          const SizedBox(height: 32),
          SizedBox(
            width: double.infinity,
            child: ElevatedButton(
              onPressed: _isLoading ? null : _submitForm,
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.blue,
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(vertical: 16),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
              ),
              child: _isLoading
                  ? const SizedBox(
                      width: 20,
                      height: 20,
                      child: CircularProgressIndicator(strokeWidth: 2, valueColor: AlwaysStoppedAnimation<Color>(Colors.white)),
                    )
                  : const Text('Create Account'),
            ),
          ),
          const SizedBox(height: 16),
        ],
      ),
      ),
    );
  }

  Widget _buildSectionHeader(String title) {
    return Text(
      title,
      style: TextStyle(fontSize: 18, fontWeight: FontWeight.w600, color: Colors.blue.shade800),
    );
  }

  Widget _buildAnimatedBackground() {
    return AnimatedBuilder(
      animation: Listenable.merge([_particleAnimation, _gradientAnimation]),
      builder: (context, child) {
        return Container(
          decoration: BoxDecoration(
            gradient: LinearGradient(
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
              colors: [
                Colors.blue.shade50,
                Colors.blue.shade100,
                Colors.white,
                Colors.blue.shade50,
              ],
              stops: [
                0.0,
                0.3 + (_gradientAnimation.value * 0.2),
                0.7 + (_gradientAnimation.value * 0.2),
                1.0,
              ],
            ),
          ),
          child: CustomPaint(
            painter: ParticlePainter(
              animation: _particleAnimation,
            ),
            size: Size.infinite,
          ),
        );
      },
    );
  }
}

class ParticlePainter extends CustomPainter {
  final Animation<double> animation;

  ParticlePainter({required this.animation}) : super(repaint: animation);

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = Colors.blue.withOpacity(0.1)
      ..style = PaintingStyle.fill;

    final random = math.Random(42); // Fixed seed for consistent animation
    
    for (int i = 0; i < 50; i++) {
      final x = (random.nextDouble() * size.width);
      final y = (random.nextDouble() * size.height);
      final radius = 2 + (random.nextDouble() * 3);
      
      // Animate particles with different speeds
      final offsetX = math.sin(animation.value * 2 * math.pi + i * 0.5) * 20;
      final offsetY = math.cos(animation.value * 2 * math.pi + i * 0.3) * 15;
      
      canvas.drawCircle(
        Offset(x + offsetX, y + offsetY),
        radius,
        paint,
      );
    }

    // Add some floating geometric shapes
    final shapePaint = Paint()
      ..color = Colors.blue.withOpacity(0.05)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 1;

    // Animated circles
    for (int i = 0; i < 8; i++) {
      final centerX = size.width * (0.1 + i * 0.1);
      final centerY = size.height * (0.2 + i * 0.15);
      final radius = 30 + (math.sin(animation.value * 2 * math.pi + i) * 10);
      
      canvas.drawCircle(
        Offset(centerX, centerY),
        radius,
        shapePaint,
      );
    }

    // Animated rectangles
    for (int i = 0; i < 5; i++) {
      final left = size.width * (0.05 + i * 0.2);
      final top = size.height * (0.1 + i * 0.25);
      final width = 40 + (math.cos(animation.value * 2 * math.pi + i) * 15);
      final height = 30 + (math.sin(animation.value * 2 * math.pi + i) * 10);
      
      canvas.drawRect(
        Rect.fromLTWH(left, top, width, height),
        shapePaint,
      );
    }
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => true;
}
