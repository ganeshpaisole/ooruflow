import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'config/theme.dart';
import 'providers/auth_provider.dart';
import 'providers/ride_provider.dart';
import 'screens/auth/login_screen.dart';
import 'screens/rider/home_screen.dart';
import 'screens/driver/driver_home_screen.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(
    MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => AuthProvider()),
        ChangeNotifierProvider(create: (_) => RideProvider()),
      ],
      child: const OoruFlowApp(),
    ),
  );
}

class OoruFlowApp extends StatelessWidget {
  const OoruFlowApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'OoruFlow',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.light,
      home: const _Splash(),
    );
  }
}

class _Splash extends StatefulWidget {
  const _Splash();
  @override
  State<_Splash> createState() => _SplashState();
}

class _SplashState extends State<_Splash> {
  @override
  void initState() {
    super.initState();
    _navigate();
  }

  Future<void> _navigate() async {
    await Future.delayed(const Duration(milliseconds: 800));
    if (!mounted) return;
    final auth = context.read<AuthProvider>();
    await auth.checkAuth();
    if (!mounted) return;
    if (auth.isLoggedIn) {
      Navigator.pushReplacement(context, MaterialPageRoute(
        builder: (_) => auth.isDriver ? const DriverHomeScreen() : const RiderHomeScreen(),
      ));
    } else {
      Navigator.pushReplacement(context, MaterialPageRoute(builder: (_) => const LoginScreen()));
    }
  }

  @override
  Widget build(BuildContext context) {
    return const Scaffold(
      body: Center(child: Column(mainAxisAlignment: MainAxisAlignment.center, children: [
        Text('🚗', style: TextStyle(fontSize: 64)),
        SizedBox(height: 16),
        Text('OoruFlow', style: TextStyle(fontSize: 28, fontWeight: FontWeight.bold, color: Color(0xFFC2410C))),
        SizedBox(height: 8),
        Text('Bengaluru Office Commute', style: TextStyle(color: Colors.grey)),
        SizedBox(height: 40),
        CircularProgressIndicator(color: Color(0xFFF97316)),
      ])),
    );
  }
}
