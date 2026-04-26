class User {
  final int id;
  final String fullName;
  final String email;
  final String? phone;
  final String role;
  final bool isActive;

  const User({
    required this.id, required this.fullName, required this.email,
    this.phone, required this.role, required this.isActive,
  });

  factory User.fromJson(Map<String, dynamic> json) => User(
    id: json['id'], fullName: json['full_name'], email: json['email'],
    phone: json['phone'], role: json['role'], isActive: json['is_active'],
  );
}
