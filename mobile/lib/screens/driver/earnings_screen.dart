import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../../services/api_service.dart';

class EarningsScreen extends StatefulWidget {
  const EarningsScreen({super.key});
  @override
  State<EarningsScreen> createState() => _EarningsScreenState();
}

class _EarningsScreenState extends State<EarningsScreen> {
  final _api = ApiService();
  String _period = 'week';
  Map<String, dynamic>? _data;
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() => _loading = true);
    try {
      final data = await _api.get('/drivers/me/earnings?period=\$_period');
      setState(() { _data = data; _loading = false; });
    } catch (_) { setState(() => _loading = false); }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('My Earnings')),
      body: Padding(padding: const EdgeInsets.all(16), child: Column(children: [
        Row(mainAxisAlignment: MainAxisAlignment.center, children: [
          for (final p in ['week', 'month', 'all'])
            Padding(padding: const EdgeInsets.symmetric(horizontal: 4),
              child: ChoiceChip(label: Text(p.capitalize()), selected: _period == p,
                selectedColor: const Color(0xFFF97316), onSelected: (_) {
                  setState(() => _period = p); _load();
                })),
        ]),
        const SizedBox(height: 20),
        if (_loading) const Center(child: CircularProgressIndicator())
        else if (_data != null) ...[
          Container(width: double.infinity, padding: const EdgeInsets.all(24),
            decoration: BoxDecoration(gradient: const LinearGradient(
              colors: [Color(0xFFF97316), Color(0xFFEA580C)]),
              borderRadius: BorderRadius.circular(16)),
            child: Column(children: [
              const Text('Total Earnings', style: TextStyle(color: Colors.white70, fontSize: 14)),
              const SizedBox(height: 8),
              Text('₹\${(_data!['total_earnings'] as num).toStringAsFixed(2)}',
                style: const TextStyle(color: Colors.white, fontSize: 36, fontWeight: FontWeight.bold)),
              const SizedBox(height: 4),
              Text('\${_data!['total_rides']} rides completed',
                style: const TextStyle(color: Colors.white70, fontSize: 13)),
            ])),
          const SizedBox(height: 20),
          Expanded(child: ListView.builder(
            itemCount: (_data!['earnings'] as List).length,
            itemBuilder: (_, i) {
              final e = (_data!['earnings'] as List)[i];
              return ListTile(
                title: Text('Ride #\${e['ride_id']}'),
                subtitle: Text(DateFormat('dd MMM, h:mm a').format(DateTime.parse(e['date']).toLocal())),
                trailing: Text('₹\${(e['amount'] as num).toStringAsFixed(2)}',
                  style: const TextStyle(fontWeight: FontWeight.bold, color: Color(0xFF16A34A))),
              );
            })),
        ],
      ])),
    );
  }
}

extension StringExt on String {
  String capitalize() => isEmpty ? this : '\${this[0].toUpperCase()}\${substring(1)}';
}
