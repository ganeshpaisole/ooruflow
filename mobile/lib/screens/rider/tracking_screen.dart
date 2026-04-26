import 'package:flutter/material.dart';
import 'package:web_socket_channel/web_socket_channel.dart';
import 'dart:convert';
import 'package:google_maps_flutter/google_maps_flutter.dart';
import '../../models/ride.dart';
import '../../config/api_config.dart';

class TrackingScreen extends StatefulWidget {
  final Ride ride;
  final String token;
  const TrackingScreen({super.key, required this.ride, required this.token});
  @override
  State<TrackingScreen> createState() => _TrackingScreenState();
}

class _TrackingScreenState extends State<TrackingScreen> {
  late WebSocketChannel _channel;
  LatLng? _driverLocation;
  GoogleMapController? _mapController;

  @override
  void initState() {
    super.initState();
    final wsUrl = ApiConfig.baseUrl.replaceFirst('http', 'ws');
    _channel = WebSocketChannel.connect(
      Uri.parse('\$wsUrl/ws/rides/\${widget.ride.id}/track?token=\${widget.token}'),
    );
    _channel.stream.listen((msg) {
      final data = jsonDecode(msg);
      if (data['type'] == 'location') {
        setState(() => _driverLocation = LatLng(data['lat'], data['lng']));
        _mapController?.animateCamera(CameraUpdate.newLatLng(_driverLocation!));
      }
    });
  }

  @override
  void dispose() {
    _channel.sink.close();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Live Tracking')),
      body: Stack(children: [
        GoogleMap(
          initialCameraPosition: CameraPosition(
            target: LatLng(
              widget.ride.pickupLat ?? 12.9716,
              widget.ride.pickupLng ?? 77.5946,
            ),
            zoom: 14,
          ),
          onMapCreated: (c) => _mapController = c,
          markers: {
            if (_driverLocation != null)
              Marker(markerId: const MarkerId('driver'), position: _driverLocation!,
                icon: BitmapDescriptor.defaultMarkerWithHue(BitmapDescriptor.hueOrange),
                infoWindow: const InfoWindow(title: 'Your Driver')),
            if (widget.ride.pickupLat != null)
              Marker(markerId: const MarkerId('pickup'),
                position: LatLng(widget.ride.pickupLat!, widget.ride.pickupLng!),
                icon: BitmapDescriptor.defaultMarkerWithHue(BitmapDescriptor.hueGreen),
                infoWindow: const InfoWindow(title: 'Your Pickup')),
          },
        ),
        Positioned(bottom: 0, left: 0, right: 0,
          child: Container(
            margin: const EdgeInsets.all(16),
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(16),
              boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.1), blurRadius: 10)]),
            child: Column(crossAxisAlignment: CrossAxisAlignment.start, mainAxisSize: MainAxisSize.min, children: [
              Text(widget.ride.status == 'confirmed' ? '🚗 Driver on the way' : '📍 Ride in progress',
                style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
              const SizedBox(height: 6),
              Text('\${widget.ride.pickupLocation} → \${widget.ride.dropoffLocation}',
                style: TextStyle(color: Colors.grey[600], fontSize: 13)),
              if (_driverLocation == null)
                const Padding(padding: EdgeInsets.only(top: 8),
                  child: Text('Waiting for driver location…', style: TextStyle(color: Colors.orange))),
            ]),
          )),
      ]),
    );
  }
}
