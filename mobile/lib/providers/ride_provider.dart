import 'package:flutter/material.dart';
import '../models/ride.dart';
import '../services/api_service.dart';

class RideProvider extends ChangeNotifier {
  final _api = ApiService();

  List<Ride> _rides = [];
  bool _loading = false;
  String? _error;

  List<Ride> get rides => _rides;
  List<Ride> get upcoming => _rides.where((r) => r.isUpcoming).toList();
  List<Ride> get past => _rides.where((r) => !r.isUpcoming).toList();
  bool get loading => _loading;
  String? get error => _error;

  Future<void> fetchRides() async {
    _loading = true; notifyListeners();
    try {
      final data = await _api.get('/rides/') as List;
      _rides = data.map((j) => Ride.fromJson(j)).toList();
      _error = null;
    } catch (e) {
      _error = e.toString().replaceAll('Exception: ', '');
    }
    _loading = false; notifyListeners();
  }

  Future<Map<String, dynamic>?> estimateFare({
    required double pickupLat, required double pickupLng,
    required double dropoffLat, required double dropoffLng,
    required String rideType, required String slotStart,
  }) async {
    try {
      final params = '?pickup_lat=\$pickupLat&pickup_lng=\$pickupLng'
          '&dropoff_lat=\$dropoffLat&dropoff_lng=\$dropoffLng'
          '&ride_type=\$rideType&slot_start=\$slotStart';
      final data = await _api.get('/rides/estimate\$params');
      return data as Map<String, dynamic>;
    } catch (_) { return null; }
  }

  Future<Ride?> bookRide(Map<String, dynamic> payload) async {
    try {
      final data = await _api.post('/rides/', payload);
      final ride = Ride.fromJson(data);
      _rides.insert(0, ride);
      notifyListeners();
      return ride;
    } catch (e) {
      _error = e.toString().replaceAll('Exception: ', '');
      notifyListeners();
      return null;
    }
  }

  Future<bool> cancelRide(int rideId) async {
    try {
      await _api.patch('/rides/\$rideId/cancel', {});
      _rides.removeWhere((r) => r.id == rideId);
      notifyListeners();
      return true;
    } catch (_) { return false; }
  }
}
