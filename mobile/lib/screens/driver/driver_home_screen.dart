import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:geolocator/geolocator.dart';
import '../../providers/auth_provider.dart';
import '../../services/api_service.dart';
import 'earnings_screen.dart';

class DriverHomeScreen extends StatefulWidget {
  const DriverHomeScreen({super.key});
  @override
  State<DriverHomeScreen> createState() => _DriverHomeScreenState();
}

class _DriverHomeScreenState extends State<DriverHomeScreen> {
  final _api = ApiService();
  bool _online = false;
  bool _toggling = false;
  List _assignedRides = [];

  @override
  void initState() {
    super.initState();
    _loadProfile();
  }

  Future<void> _loadProfile() async {
    try {
      final driver = await _api.get('/drivers/me');
      setState(() => _online = driver['status'] == 'online');
      final rides = await _api.get('/rides/');
      setState(() => _assignedRides = (rides as List).where((r) =>
        r['status'] == 'confirmed' || r['status'] == 'in_progress').toList());
    } catch (_) {}
  }

  Future<void> _toggleOnline() async {
    setState(() => _toggling = true);
    try {
      final newStatus = _online ? 'offline' : 'online';
      await _api.patch('/drivers/me/status', {'status': newStatus});
      setState(() => _online = !_online);
      if (_online) _startLocationUpdates();
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(e.toString())));
    }
    setState(() => _toggling = false);
  }

  void _startLocationUpdates() async {
    final permission = await Geolocator.requestPermission();
    if (permission == LocationPermission.denied) return;
    Geolocator.getPositionStream(
      locationSettings: const LocationSettings(accuracy: LocationAccuracy.high, distanceFilter: 20),
    ).listen((pos) async {
      try {
        await _api.patch('/drivers/me/location', {'lat': pos.latitude, 'lng': pos.longitude});
      } catch (_) {}
    });
  }

  @override
  Widget build(BuildContext context) {
    final auth = context.watch<AuthProvider>();
    return Scaffold(
      appBar: AppBar(
        title: const Text('Driver Dashboard'),
        actions: [
          IconButton(icon: const Icon(Icons.bar_chart_outlined),
            onPressed: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const EarningsScreen()))),
          IconButton(icon: const Icon(Icons.logout_outlined), onPressed: () => auth.logout()),
        ],
      ),
      body: Padding(padding: const EdgeInsets.all(20), child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // Online/Offline toggle
          Container(padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              color: _online ? const Color(0xFFDCFCE7) : const Color(0xFFF3F4F6),
              borderRadius: BorderRadius.circular(16)),
            child: Row(mainAxisAlignment: MainAxisAlignment.spaceBetween, children: [
              Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                Text(_online ? 'You are ONLINE' : 'You are OFFLINE',
                  style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18,
                    color: _online ? const Color(0xFF16A34A) : Colors.grey[700])),
                const SizedBox(height: 4),
                Text(_online ? 'Ready to receive rides' : 'Go online to accept rides',
                  style: TextStyle(color: Colors.grey[600], fontSize: 13)),
              ]),
              _toggling
                ? const CircularProgressIndicator()
                : Switch(value: _online, onChanged: (_) => _toggleOnline(),
                    activeColor: const Color(0xFF16A34A)),
            ])),
          const SizedBox(height: 24),
          const Text('Assigned Rides', style: TextStyle(fontSize: 17, fontWeight: FontWeight.bold)),
          const SizedBox(height: 12),
          Expanded(child: _assignedRides.isEmpty
            ? Center(child: Text('No rides assigned yet', style: TextStyle(color: Colors.grey[500])))
            : ListView.builder(
                itemCount: _assignedRides.length,
                itemBuilder: (_, i) {
                  final r = _assignedRides[i];
                  return Card(margin: const EdgeInsets.symmetric(vertical: 6),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                    child: ListTile(
                      title: Text('\${r['pickup_location']} → \${r['dropoff_location']}'),
                      subtitle: Text('Status: \${r['status']} · ₹\${r['fare'] ?? 'TBD'}'),
                      leading: const Icon(Icons.directions_car, color: Color(0xFFF97316)),
                    ));
                })),
        ],
      )),
    );
  }
}
