import 'package:flutter/material.dart';
import 'dashboard_screen.dart';
import 'log_vitals_screen.dart';
import 'detailed_report_screen.dart';
import 'emergency_guidance_screen.dart';
import 'tips_data.dart';
import 'tips_details.dart';

class MainScreen extends StatefulWidget {
  const MainScreen({super.key});

  @override
  State<MainScreen> createState() => _MainScreenState();
}

class _MainScreenState extends State<MainScreen> {
  int _selectedIndex = 0;

  late final List<Widget> _screens = [
    const DashboardScreen(),
    const LogVitalsScreen(),
    const DetailedReportScreen(),
    const EmergencyGuidanceScreen(),
    LifestyleTipDetailScreen(tipId: lifestyleTips.first.id),
  ];

  void _onItemTapped(int index) => setState(() => _selectedIndex = index);

  @override
Widget build(BuildContext context) {
  return Scaffold(
    body: _screens[_selectedIndex],
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
          icon: Icon(Icons.add_circle_outline),
          activeIcon: Icon(Icons.favorite_outline, color: Colors.green),
          label: 'Log Vitals',
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