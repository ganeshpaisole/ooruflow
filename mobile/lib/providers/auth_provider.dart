import 'package:flutter/material.dart';
import '../models/user.dart';
import '../services/auth_service.dart';
import '../services/api_service.dart';

class AuthProvider extends ChangeNotifier {
  final _authService = AuthService();
  final _api = ApiService();

  User? _user;
  bool _loading = false;
  String? _error;

  User? get user => _user;
  bool get loading => _loading;
  String? get error => _error;
  bool get isLoggedIn => _user != null;
  bool get isDriver => _user?.role == 'driver';
  bool get isAdmin => _user?.role == 'admin';

  Future<void> checkAuth() async {
    if (!await _authService.isLoggedIn()) return;
    try {
      // Decode user from existing token (lightweight check)
      _loading = true; notifyListeners();
      final rides = await _api.get('/rides/');
      // If token is valid, we're logged in — fetch user from token claims
      _loading = false; notifyListeners();
    } catch (_) {
      await _authService.logout();
      _loading = false; notifyListeners();
    }
  }

  Future<bool> login(String email, String password) async {
    _loading = true; _error = null; notifyListeners();
    try {
      await _authService.login(email, password);
      _loading = false; notifyListeners();
      return true;
    } catch (e) {
      _error = e.toString().replaceAll('Exception: ', '');
      _loading = false; notifyListeners();
      return false;
    }
  }

  Future<bool> signup(String fullName, String email, String password, String? phone) async {
    _loading = true; _error = null; notifyListeners();
    try {
      _user = await _authService.signup(fullName, email, password, phone);
      _loading = false; notifyListeners();
      return true;
    } catch (e) {
      _error = e.toString().replaceAll('Exception: ', '');
      _loading = false; notifyListeners();
      return false;
    }
  }

  Future<void> logout() async {
    await _authService.logout();
    _user = null; notifyListeners();
  }
}
