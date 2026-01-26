import 'package:flutter/material.dart';
import 'package:myapp/screens/main_screen.dart';
import 'package:myapp/screens/login_screen.dart';
import 'models/notifications_service.dart'; 
import 'dart:async';
import 'package:provider/provider.dart';
import 'providers/auth_provider.dart';
import 'providers/vitals_provider.dart';
import 'providers/medication_provider.dart';
import 'providers/notification_provider.dart';
import 'providers/appointment_provider.dart';
import 'services/notification_polling_service.dart';
import 'theme/app_theme.dart';
import 'api/api_service.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();

  FlutterError.onError = (FlutterErrorDetails details) {
    FlutterError.presentError(details);
    debugPrint("Flutter error caught: ${details.exceptionAsString()}");
  };

  await NotificationsService.initialize();
  runApp(const MyApp());
}




class MyApp extends StatelessWidget {
  const MyApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => AuthProvider()),
        ChangeNotifierProvider(create: (_) => VitalsProvider()),
        ChangeNotifierProxyProvider<AuthProvider, MedicationProvider>(
          create: (_) => MedicationProvider(apiBaseUrl: ApiService.baseUrl, token: ""),
          update: (_, authProvider, previous) => MedicationProvider(
            apiBaseUrl: ApiService.baseUrl,
            token: authProvider.token ?? "",
          ),
        ),
        ChangeNotifierProxyProvider<AuthProvider, NotificationProvider>(
          create: (_) => NotificationProvider(apiBaseUrl: ApiService.baseUrl, token: ""),
          update: (_, authProvider, previous) => NotificationProvider(
            apiBaseUrl: ApiService.baseUrl,
            token: authProvider.token ?? "",
          ),
        ),
        ChangeNotifierProxyProvider<AuthProvider, AppointmentProvider>(
          create: (_) => AppointmentProvider(apiBaseUrl: ApiService.baseUrl, token: ""),
          update: (_, authProvider, previous) => previous!..update(ApiService.baseUrl, authProvider.token ?? ""),
        ),
      ],
      




      child: Consumer<AuthProvider>(
        builder: (context, authProvider, child) {
          return MaterialApp(
            title: 'Hypertension Care',
            debugShowCheckedModeBanner: false,
            theme: AppTheme.lightTheme,
            home: const AuthWrapper(),
          );
        },
      ),
    );
  }
}

class AuthWrapper extends StatefulWidget {
  const AuthWrapper({Key? key}) : super(key: key);

  @override
  State<AuthWrapper> createState() => _AuthWrapperState();
}

class _AuthWrapperState extends State<AuthWrapper> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<AuthProvider>().initializeAuth();
      _initializePolling();
    });
  }

  void _initializePolling() {
    Future.delayed(Duration.zero, () {
      // FIX #1: Immediate sanity test notification
      NotificationsService.showInstantNotification(
        id: 999,
        title: 'Test Notification',
        body: 'notifications best.',
      );
    });
  }

  @override
  void dispose() {
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Consumer<AuthProvider>(
      builder: (context, authProvider, child) {
        if (authProvider.isLoading && !authProvider.isLoggedIn) {
          return const Scaffold(
            body: Center(child: CircularProgressIndicator()),
          );
        }
        
        return authProvider.isLoggedIn ? const MainScreen() : const LoginScreen();
      },
    );
  }
}



