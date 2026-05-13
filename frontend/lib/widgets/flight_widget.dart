import 'package:flutter/material.dart';

class FlightWidget extends StatelessWidget {
  final List<dynamic> flights;

  const FlightWidget({super.key, required this.flights});

  @override
  Widget build(BuildContext context) {
    if (flights.isEmpty) {
      return const Card(
        child: Padding(
          padding: EdgeInsets.all(16),
          child: Text('No flights found.'),
        ),
      );
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Padding(
          padding: EdgeInsets.only(left: 4, bottom: 8),
          child: Text(
            'Flights',
            style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
          ),
        ),
        ...flights.map((f) => _FlightCard(flight: f)),
      ],
    );
  }
}

class _FlightCard extends StatelessWidget {
  final dynamic flight;

  const _FlightCard({required this.flight});

  @override
  Widget build(BuildContext context) {
    final airline = flight['airline'] as String? ?? '';
    final flightNum = flight['flight_number'] as String? ?? '';
    final departure = flight['departure'] as String? ?? '';
    final arrival = flight['arrival'] as String? ?? '';
    final price = (flight['price'] as num?)?.toDouble() ?? 0;
    final duration = flight['duration'] as String? ?? '';

    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Row(
          children: [
            Container(
              width: 60,
              height: 60,
              decoration: BoxDecoration(
                color: Colors.orange.shade100,
                borderRadius: BorderRadius.circular(8),
              ),
              child: Icon(
                Icons.flight,
                color: Colors.orange.shade700,
                size: 32,
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    '$airline ($flightNum)',
                    style: const TextStyle(
                      fontWeight: FontWeight.bold,
                      fontSize: 15,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    '$departure → $arrival ($duration)',
                    style: TextStyle(color: Colors.grey.shade600, fontSize: 13),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    '\u20b9${price.toStringAsFixed(0)}',
                    style: TextStyle(
                      color: Colors.green.shade700,
                      fontWeight: FontWeight.w600,
                      fontSize: 14,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
