import 'package:flutter/material.dart';
import 'package:myapp/main_screen.dart';
import 'package:myapp/login_screen.dart';
import 'notifications_service.dart'; 
import 'dart:async';
import 'package:provider/provider.dart';
import 'providers/auth_provider.dart';
import 'providers/vitals_provider.dart';
import 'providers/medication_provider.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();

  FlutterError.onError = (FlutterErrorDetails details) {
    FlutterError.presentError(details);
    debugPrint("Flutter error caught: ${details.exceptionAsString()}");
  };

  runZonedGuarded<Future<void>>(() async {
    await NotificationsService.initialize();
    runApp(const MyApp());
  }, (error, stack) {
    debugPrint("Uncaught async error: $error");
    debugPrint("Stack trace: $stack");
  });
}




class MyApp extends StatelessWidget {
  const MyApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => AuthProvider()),
        ChangeNotifierProvider(create: (_) => VitalsProvider()),
        ChangeNotifierProvider(create: (_) => MedicationProvider()),
      ],
      child: Consumer<AuthProvider>(
        builder: (context, authProvider, child) {
          return MaterialApp(
            title: 'My App',
            debugShowCheckedModeBanner: false,
            theme: ThemeData(primarySwatch: Colors.blue),
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
    });
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



