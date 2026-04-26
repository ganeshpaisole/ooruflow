import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/ride_provider.dart';
import '../../widgets/ride_card.dart';

class MyRidesScreen extends StatefulWidget {
  const MyRidesScreen({super.key});
  @override
  State<MyRidesScreen> createState() => _MyRidesScreenState();
}

class _MyRidesScreenState extends State<MyRidesScreen> with SingleTickerProviderStateMixin {
  late TabController _tabs;

  @override
  void initState() {
    super.initState();
    _tabs = TabController(length: 2, vsync: this);
  }

  @override
  Widget build(BuildContext context) {
    final rides = context.watch<RideProvider>();
    return Column(children: [
      TabBar(controller: _tabs,
        labelColor: const Color(0xFFF97316),
        indicatorColor: const Color(0xFFF97316),
        tabs: const [Tab(text: 'Upcoming'), Tab(text: 'History')]),
      Expanded(child: TabBarView(controller: _tabs, children: [
        rides.loading
          ? const Center(child: CircularProgressIndicator())
          : rides.upcoming.isEmpty
            ? const Center(child: Text('No upcoming rides'))
            : ListView.builder(padding: const EdgeInsets.all(12),
                itemCount: rides.upcoming.length,
                itemBuilder: (_, i) => RideCard(ride: rides.upcoming[i])),
        rides.past.isEmpty
          ? const Center(child: Text('No ride history'))
          : ListView.builder(padding: const EdgeInsets.all(12),
              itemCount: rides.past.length,
              itemBuilder: (_, i) => RideCard(ride: rides.past[i])),
      ])),
    ]);
  }
}
