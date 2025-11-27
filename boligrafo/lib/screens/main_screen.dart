import 'package:flutter/material.dart';
import 'package:myapp/screens/medication_screen.dart';
import 'dashboard_screen.dart';
import 'log_vitals_screen.dart';
import 'detailed_report_screen.dart';
import 'emergency_guidance_screen.dart';


class MainScreen extends StatefulWidget {
  const MainScreen({super.key});

  @override
  State<MainScreen> createState() => _MainScreenState();
}

class _MainScreenState extends State<MainScreen> {
  int _selectedIndex = 0;

  late final PageController _pageController;

  @override
  void initState() {
    super.initState();
    _pageController = PageController();
  }

  late final List<Widget> _screens = [
    const DashboardScreen(),
    const MedicationScreen(),
    const LogVitalsScreen(),
    const DetailedReportScreen(),
    const EmergencyGuidanceScreen(),
  ];

  void _onItemTapped(int index) {
    setState(() => _selectedIndex = index);
    _pageController.animateToPage(
      index,
      duration: const Duration(milliseconds: 300),
      curve: Curves.easeInOut,
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: PageView(
        controller: _pageController,
        onPageChanged: (index) {
          setState(() => _selectedIndex = index);
        },
        children: _screens,
      ),
      bottomNavigationBar: BottomNavigationBar(
        type: BottomNavigationBarType.fixed,
        currentIndex: _selectedIndex,
        selectedItemColor: Colors.green,
        unselectedItemColor: Colors.grey,
        showUnselectedLabels: true,
        onTap: _onItemTapped,
        items: const [
          BottomNavigationBarItem(
            icon: Icon(Icons.dashboard_customize_outlined),
            activeIcon: Icon(Icons.dashboard_customize, color: Colors.green),
            label: 'Dashboard',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.medical_services_outlined),
            activeIcon: Icon(Icons.medication, color: Colors.green),
            label: 'Prescriptions',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.add_circle_outline),
            activeIcon: Icon(Icons.favorite_outline, color: Colors.green),
            label: 'logvitals',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.insights_outlined),
            activeIcon: Icon(Icons.insights, color: Colors.green),
            label: 'Reports',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.health_and_safety_outlined),
            activeIcon: Icon(Icons.health_and_safety, color: Colors.red),
            label: 'Emergency',
          ),
        ],
      ),
    );
  }
}
