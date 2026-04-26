import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:intl/intl.dart';
import '../../providers/ride_provider.dart';
import '../../widgets/app_button.dart';

class BookRideScreen extends StatefulWidget {
  const BookRideScreen({super.key});
  @override
  State<BookRideScreen> createState() => _BookRideScreenState();
}

class _BookRideScreenState extends State<BookRideScreen> {
  final _pickupCtrl  = TextEditingController();
  final _dropoffCtrl = TextEditingController();
  DateTime _slotDate = DateTime.now().add(const Duration(days: 1));
  TimeOfDay _startTime = const TimeOfDay(hour: 9, minute: 0);
  TimeOfDay _endTime   = const TimeOfDay(hour: 9, minute: 30);
  String _rideType = 'solo';
  Map<String, dynamic>? _estimate;
  bool _booking = false;

  String _fmt(DateTime d) => DateFormat('yyyy-MM-dd').format(d);
  String _fmtTime(TimeOfDay t) => '\${t.hour.toString().padLeft(2,'0')}:\${t.minute.toString().padLeft(2,'0')}';

  Future<void> _book() async {
    if (_pickupCtrl.text.isEmpty || _dropoffCtrl.text.isEmpty) return;
    setState(() => _booking = true);
    final iso = '\${_fmt(_slotDate)}T\${_fmtTime(_startTime)}:00+05:30';
    final isoEnd = '\${_fmt(_slotDate)}T\${_fmtTime(_endTime)}:00+05:30';
    final ride = await context.read<RideProvider>().bookRide({
      'pickup_location': _pickupCtrl.text,
      'dropoff_location': _dropoffCtrl.text,
      'slot_start': iso, 'slot_end': isoEnd,
      'ride_type': _rideType,
    });
    setState(() => _booking = false);
    if (!mounted) return;
    if (ride != null) {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Ride booked! Confirmation by 8 PM IST.')));
      _pickupCtrl.clear(); _dropoffCtrl.clear();
    } else {
      final err = context.read<RideProvider>().error;
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(err ?? 'Booking failed')));
    }
  }

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(padding: const EdgeInsets.all(20), child: Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        const Text('Book a Ride', style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold)),
        const SizedBox(height: 4),
        Text('Closes at 8 PM IST', style: TextStyle(color: Colors.grey[600], fontSize: 13)),
        const SizedBox(height: 24),
        TextField(controller: _pickupCtrl, decoration: const InputDecoration(labelText: 'Pickup Location', prefixIcon: Icon(Icons.my_location))),
        const SizedBox(height: 14),
        TextField(controller: _dropoffCtrl, decoration: const InputDecoration(labelText: 'Dropoff Location', prefixIcon: Icon(Icons.location_on_outlined))),
        const SizedBox(height: 20),
        ListTile(
          contentPadding: EdgeInsets.zero,
          leading: const Icon(Icons.calendar_today_outlined),
          title: Text(DateFormat('EEE, dd MMM yyyy').format(_slotDate)),
          trailing: const Icon(Icons.chevron_right),
          onTap: () async {
            final picked = await showDatePicker(context: context,
              initialDate: _slotDate,
              firstDate: DateTime.now().add(const Duration(days: 1)),
              lastDate: DateTime.now().add(const Duration(days: 30)));
            if (picked != null) setState(() => _slotDate = picked);
          },
        ),
        Row(children: [
          Expanded(child: ListTile(contentPadding: EdgeInsets.zero,
            leading: const Icon(Icons.schedule),
            title: Text('From \${_fmtTime(_startTime)}'),
            onTap: () async {
              final t = await showTimePicker(context: context, initialTime: _startTime);
              if (t != null) setState(() => _startTime = t);
            })),
          Expanded(child: ListTile(contentPadding: EdgeInsets.zero,
            title: Text('To \${_fmtTime(_endTime)}'),
            onTap: () async {
              final t = await showTimePicker(context: context, initialTime: _endTime);
              if (t != null) setState(() => _endTime = t);
            })),
        ]),
        const SizedBox(height: 16),
        Row(children: [
          Expanded(child: _TypeButton(label: '🚗 Solo', value: 'solo', selected: _rideType, onTap: () => setState(() => _rideType = 'solo'))),
          const SizedBox(width: 12),
          Expanded(child: _TypeButton(label: '🤝 Pool', value: 'pool', selected: _rideType, onTap: () => setState(() => _rideType = 'pool'))),
        ]),
        const SizedBox(height: 28),
        AppButton(label: 'Confirm Booking', onPressed: _book, loading: _booking),
      ],
    ));
  }
}

class _TypeButton extends StatelessWidget {
  final String label, value, selected;
  final VoidCallback onTap;
  const _TypeButton({required this.label, required this.value, required this.selected, required this.onTap});

  @override
  Widget build(BuildContext context) {
    final isSelected = value == selected;
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 14),
        decoration: BoxDecoration(
          color: isSelected ? const Color(0xFFF97316) : Colors.white,
          border: Border.all(color: isSelected ? const Color(0xFFF97316) : Colors.grey[300]!),
          borderRadius: BorderRadius.circular(10),
        ),
        child: Text(label, textAlign: TextAlign.center,
          style: TextStyle(fontWeight: FontWeight.w600, color: isSelected ? Colors.white : Colors.grey[700])),
      ),
    );
  }
}
