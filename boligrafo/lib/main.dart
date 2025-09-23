import 'package:flutter/material.dart';
import 'package:myapp/main_screen.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:myapp/login_screen.dart';
import 'login_screen.dart';
import 'notifications_service.dart'; 
import 'dart:async';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();

  FlutterError.onError = (FlutterErrorDetails details) {
    FlutterError.presentError(details); 
    debugPrint("Flutter error caught: ${details.exceptionAsString()}");
  };

  runZonedGuarded<Future<void>>(() async {
    await NotificationsService.initialize();

    final prefs = await SharedPreferences.getInstance();
    final loggedIn = prefs.getBool('loggedIn') ?? false;

    runApp(MyApp(loggedIn: loggedIn));
  }, (error, stack) {
    debugPrint("Uncaught async error: $error");
    debugPrint("Stack trace: $stack");
  });
}

class MyApp extends StatelessWidget {
  final bool loggedIn;

  const MyApp({Key? key, required this.loggedIn}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'My App',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(primarySwatch: Colors.blue),
      home: loggedIn ? const HomeScreen() : const LoginScreen(),
    );
  }
}

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Home')),
      body: const Center(child: Text('Welcome!')),
    );
  }
}
