class Ride {
  final int id;
  final int userId;
  final int? driverId;
  final String rideType;
  final String pickupLocation;
  final String dropoffLocation;
  final double? pickupLat;
  final double? pickupLng;
  final double? dropoffLat;
  final double? dropoffLng;
  final DateTime slotStart;
  final DateTime slotEnd;
  final String status;
  final double? fare;
  final String paymentStatus;
  final DateTime createdAt;

  const Ride({
    required this.id, required this.userId, this.driverId,
    required this.rideType, required this.pickupLocation, required this.dropoffLocation,
    this.pickupLat, this.pickupLng, this.dropoffLat, this.dropoffLng,
    required this.slotStart, required this.slotEnd, required this.status,
    this.fare, required this.paymentStatus, required this.createdAt,
  });

  factory Ride.fromJson(Map<String, dynamic> json) => Ride(
    id: json['id'], userId: json['user_id'], driverId: json['driver_id'],
    rideType: json['ride_type'],
    pickupLocation: json['pickup_location'], dropoffLocation: json['dropoff_location'],
    pickupLat: json['pickup_lat']?.toDouble(), pickupLng: json['pickup_lng']?.toDouble(),
    dropoffLat: json['dropoff_lat']?.toDouble(), dropoffLng: json['dropoff_lng']?.toDouble(),
    slotStart: DateTime.parse(json['slot_start']),
    slotEnd: DateTime.parse(json['slot_end']),
    status: json['status'], fare: json['fare']?.toDouble(),
    paymentStatus: json['payment_status'],
    createdAt: DateTime.parse(json['created_at']),
  );

  bool get isUpcoming => status == 'pending' || status == 'confirmed';
  bool get isPool => rideType == 'pool';
}
