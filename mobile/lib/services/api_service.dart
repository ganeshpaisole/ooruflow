import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import '../config/api_config.dart';

class ApiService {
  static final ApiService _instance = ApiService._();
  factory ApiService() => _instance;
  ApiService._();

  Future<String?> _getToken() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString('access_token');
  }

  Future<Map<String, String>> _headers({bool form = false}) async {
    final token = await _getToken();
    return {
      'Content-Type': form ? 'application/x-www-form-urlencoded' : 'application/json',
      if (token != null) 'Authorization': 'Bearer \$token',
    };
  }

  Future<dynamic> get(String path) async {
    final resp = await http.get(
      Uri.parse('\${ApiConfig.baseUrl}\$path'),
      headers: await _headers(),
    );
    return _parse(resp);
  }

  Future<dynamic> post(String path, Map<String, dynamic> body, {bool form = false}) async {
    final resp = await http.post(
      Uri.parse('\${ApiConfig.baseUrl}\$path'),
      headers: await _headers(form: form),
      body: form ? body.map((k, v) => MapEntry(k, v.toString())) : jsonEncode(body),
    );
    return _parse(resp);
  }

  Future<dynamic> patch(String path, Map<String, dynamic> body) async {
    final resp = await http.patch(
      Uri.parse('\${ApiConfig.baseUrl}\$path'),
      headers: await _headers(),
      body: jsonEncode(body),
    );
    return _parse(resp);
  }

  dynamic _parse(http.Response resp) {
    if (resp.statusCode >= 200 && resp.statusCode < 300) {
      if (resp.body.isEmpty) return null;
      return jsonDecode(resp.body);
    }
    final detail = jsonDecode(resp.body)['detail'] ?? 'Request failed';
    throw Exception(detail);
  }
}
