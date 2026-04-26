import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/auth_provider.dart';
import '../../providers/ride_provider.dart';
import '../../widgets/ride_card.dart';
import '../../widgets/app_button.dart';
import 'book_ride_screen.dart';
import 'my_rides_screen.dart';

class RiderHomeScreen extends StatefulWidget {
  const RiderHomeScreen({super.key});
  @override
  State<RiderHomeScreen> createState() => _RiderHomeScreenState();
}

class _RiderHomeScreenState extends State<RiderHomeScreen> {
  int _tab = 0;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<RideProvider>().fetchRides();
    });
  }

  @override
  Widget build(BuildContext context) {
    final auth  = context.watch<AuthProvider>();
    final rides = context.watch<RideProvider>();

    return Scaffold(
      appBar: AppBar(
        title: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          const Text('OoruFlow', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18)),
          Text('Hi, \${auth.user?.fullName.split(' ').first ?? 'there'} 👋',
            style: const TextStyle(fontSize: 12, fontWeight: FontWeight.normal)),
        ]),
        actions: [
          IconButton(
            icon: const Icon(Icons.logout_outlined),
            onPressed: () => auth.logout(),
          ),
        ],
      ),
      body: IndexedStack(index: _tab, children: [
        // Tab 0: Upcoming rides
        rides.loading
          ? const Center(child: CircularProgressIndicator())
          : rides.upcoming.isEmpty
            ? Center(child: Column(mainAxisAlignment: MainAxisAlignment.center, children: [
                const Text('🚗', style: TextStyle(fontSize: 48)),
                const SizedBox(height: 12),
                const Text('No upcoming rides', style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600)),
                const SizedBox(height: 8),
                Text('Book by 8 PM IST for tomorrow', style: TextStyle(color: Colors.grey[600])),
                const SizedBox(height: 24),
                AppButton(label: 'Book a Ride', onPressed: () => setState(() => _tab = 1)),
              ]))
            : ListView.builder(
                padding: const EdgeInsets.all(16),
                itemCount: rides.upcoming.length,
                itemBuilder: (_, i) => RideCard(ride: rides.upcoming[i]),
              ),

        // Tab 1: Book Ride
        const BookRideScreen(),

        // Tab 2: All Rides
        const MyRidesScreen(),
      ]),
      bottomNavigationBar: NavigationBar(
        selectedIndex: _tab,
        onDestinationSelected: (i) => setState(() => _tab = i),
        destinations: const [
          NavigationDestination(icon: Icon(Icons.home_outlined), selectedIcon: Icon(Icons.home), label: 'Home'),
          NavigationDestination(icon: Icon(Icons.add_circle_outline), selectedIcon: Icon(Icons.add_circle), label: 'Book'),
          NavigationDestination(icon: Icon(Icons.history_outlined), selectedIcon: Icon(Icons.history), label: 'Rides'),
        ],
      ),
    );
  }
}
