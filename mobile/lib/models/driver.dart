class Driver {
  final int id;
  final int userId;
  final String vehicleNumber;
  final String vehicleModel;
  final String vehicleType;
  final String licenseNumber;
  final String status;
  final double? currentLat;
  final double? currentLng;
  final double avgRating;
  final int totalRides;

  const Driver({
    required this.id, required this.userId, required this.vehicleNumber,
    required this.vehicleModel, required this.vehicleType, required this.licenseNumber,
    required this.status, this.currentLat, this.currentLng,
    required this.avgRating, required this.totalRides,
  });

  factory Driver.fromJson(Map<String, dynamic> json) => Driver(
    id: json['id'], userId: json['user_id'],
    vehicleNumber: json['vehicle_number'], vehicleModel: json['vehicle_model'],
    vehicleType: json['vehicle_type'], licenseNumber: json['license_number'],
    status: json['status'],
    currentLat: json['current_lat']?.toDouble(),
    currentLng: json['current_lng']?.toDouble(),
    avgRating: (json['avg_rating'] ?? 5.0).toDouble(),
    totalRides: json['total_rides'] ?? 0,
  );

  bool get isOnline => status == 'online';
}
