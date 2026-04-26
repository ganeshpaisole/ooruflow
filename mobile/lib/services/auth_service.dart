import 'package:shared_preferences/shared_preferences.dart';
import 'api_service.dart';
import '../models/user.dart';

class AuthService {
  final _api = ApiService();

  Future<String> login(String email, String password) async {
    final data = await _api.post('/auth/login',
      {'username': email, 'password': password}, form: true);
    final token = data['access_token'] as String;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('access_token', token);
    return token;
  }

  Future<User> signup(String fullName, String email, String password, String? phone) async {
    final data = await _api.post('/auth/signup', {
      'full_name': fullName, 'email': email, 'password': password,
      if (phone != null && phone.isNotEmpty) 'phone': phone,
    });
    return User.fromJson(data);
  }

  Future<void> logout() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('access_token');
  }

  Future<bool> isLoggedIn() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.containsKey('access_token');
  }
}
