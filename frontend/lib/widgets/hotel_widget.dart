import 'package:flutter/material.dart';

class HotelWidget extends StatelessWidget {
  final List<dynamic> hotels;

  const HotelWidget({super.key, required this.hotels});

  @override
  Widget build(BuildContext context) {
    if (hotels.isEmpty) {
      return const Card(
        child: Padding(
          padding: EdgeInsets.all(16),
          child: Text('No hotels found.'),
        ),
      );
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Padding(
          padding: EdgeInsets.only(left: 4, bottom: 8),
          child: Text(
            'Hotels',
            style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
          ),
        ),
        ...hotels.map((h) => _HotelCard(hotel: h)),
      ],
    );
  }
}

class _HotelCard extends StatelessWidget {
  final dynamic hotel;

  const _HotelCard({required this.hotel});

  @override
  Widget build(BuildContext context) {
    final name = hotel['name'] as String? ?? '';
    final price = (hotel['price_per_night'] as num?)?.toDouble() ?? 0;
    final rating = (hotel['rating'] as num?)?.toDouble() ?? 0;
    final location = hotel['location'] as String? ?? '';

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
                color: Colors.blue.shade100,
                borderRadius: BorderRadius.circular(8),
              ),
              child: Icon(Icons.hotel, color: Colors.blue.shade700, size: 32),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    name,
                    style: const TextStyle(
                      fontWeight: FontWeight.bold,
                      fontSize: 15,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    location,
                    style: TextStyle(color: Colors.grey.shade600, fontSize: 13),
                  ),
                  const SizedBox(height: 4),
                  Row(
                    children: [
                      Text(
                        '\u20b9${price.toStringAsFixed(0)}/night',
                        style: TextStyle(
                          color: Colors.green.shade700,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                      const SizedBox(width: 12),
                      Icon(Icons.star, color: Colors.amber, size: 16),
                      Text(
                        rating.toStringAsFixed(1),
                        style: const TextStyle(fontSize: 13),
                      ),
                    ],
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
