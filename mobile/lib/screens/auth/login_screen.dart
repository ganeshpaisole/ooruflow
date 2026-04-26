import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/auth_provider.dart';
import '../../widgets/app_button.dart';
import 'signup_screen.dart';
import '../rider/home_screen.dart';
import '../driver/driver_home_screen.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});
  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _emailCtrl = TextEditingController();
  final _passCtrl  = TextEditingController();

  Future<void> _login() async {
    final auth = context.read<AuthProvider>();
    final ok = await auth.login(_emailCtrl.text.trim(), _passCtrl.text);
    if (!mounted) return;
    if (ok) {
      Navigator.pushReplacement(context, MaterialPageRoute(
        builder: (_) => auth.isDriver ? const DriverHomeScreen() : const RiderHomeScreen(),
      ));
    } else {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(auth.error ?? 'Login failed')));
    }
  }

  @override
  Widget build(BuildContext context) {
    final auth = context.watch<AuthProvider>();
    return Scaffold(
      backgroundColor: const Color(0xFFFFF7ED),
      body: SafeArea(child: Center(child: SingleChildScrollView(padding: const EdgeInsets.all(24), child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          const Text('🚗 OoruFlow', style: TextStyle(fontSize: 32, fontWeight: FontWeight.bold, color: Color(0xFFC2410C))),
          const SizedBox(height: 4),
          Text('Bengaluru Office Commute', style: TextStyle(color: Colors.grey[600])),
          const SizedBox(height: 40),
          TextField(controller: _emailCtrl, keyboardType: TextInputType.emailAddress,
            decoration: const InputDecoration(labelText: 'Email', prefixIcon: Icon(Icons.email_outlined))),
          const SizedBox(height: 16),
          TextField(controller: _passCtrl, obscureText: true,
            decoration: const InputDecoration(labelText: 'Password', prefixIcon: Icon(Icons.lock_outline))),
          const SizedBox(height: 24),
          AppButton(label: 'Sign In', onPressed: _login, loading: auth.loading),
          const SizedBox(height: 16),
          TextButton(
            onPressed: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const SignupScreen())),
            child: const Text("Don't have an account? Sign up"),
          ),
        ],
      )))),
    );
  }
}
