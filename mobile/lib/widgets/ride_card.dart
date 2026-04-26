import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../models/ride.dart';

class RideCard extends StatelessWidget {
  final Ride ride;
  final VoidCallback? onTap;

  const RideCard({super.key, required this.ride, this.onTap});

  Color _statusColor(String s) => switch (s) {
    'pending'    => const Color(0xFFFACC15),
    'confirmed'  => const Color(0xFF22C55E),
    'in_progress'=> const Color(0xFF3B82F6),
    'completed'  => const Color(0xFF6B7280),
    _            => const Color(0xFFEF4444),
  };

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.symmetric(vertical: 6),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      elevation: 1,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            Row(mainAxisAlignment: MainAxisAlignment.spaceBetween, children: [
              Expanded(
                child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                  Text(ride.pickupLocation, style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 15)),
                  const SizedBox(height: 2),
                  Text('→ \${ride.dropoffLocation}', style: TextStyle(color: Colors.grey[600], fontSize: 13)),
                ]),
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                decoration: BoxDecoration(
                  color: _statusColor(ride.status).withOpacity(0.15),
                  borderRadius: BorderRadius.circular(20),
                ),
                child: Text(ride.status.replaceAll('_', ' ').toUpperCase(),
                  style: TextStyle(color: _statusColor(ride.status), fontSize: 11, fontWeight: FontWeight.w700)),
              ),
            ]),
            const SizedBox(height: 10),
            Row(children: [
              Icon(Icons.schedule, size: 15, color: Colors.grey[500]),
              const SizedBox(width: 4),
              Text(DateFormat('dd MMM, h:mm a').format(ride.slotStart.toLocal()),
                style: TextStyle(color: Colors.grey[600], fontSize: 12)),
              const SizedBox(width: 12),
              Icon(ride.isPool ? Icons.people : Icons.person, size: 15, color: Colors.grey[500]),
              const SizedBox(width: 4),
              Text(ride.isPool ? 'Pool' : 'Solo', style: TextStyle(color: Colors.grey[600], fontSize: 12)),
              if (ride.fare != null) ...[
                const SizedBox(width: 12),
                Text('₹\${ride.fare!.toStringAsFixed(0)}',
                  style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 13)),
              ],
            ]),
          ]),
        ),
      ),
    );
  }
}
