import 'package:flutter/material.dart';
import 'tips_data.dart';
import 'tips_details.dart';

class LifestyleTipsScreen extends StatelessWidget {
  const LifestyleTipsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Lifestyle Tips"),
        backgroundColor: Colors.green,
      ),
      body: ListView.builder(
        itemCount: lifestyleTips.length,
        itemBuilder: (context, index) {
          final tip = lifestyleTips[index];
          return Card(
            margin: const EdgeInsets.symmetric(horizontal: 12.0, vertical: 8.0),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(12.0),
            ),
            child: ListTile(
  leading: CircleAvatar(
    backgroundColor: Colors.greenAccent,
    child: Text(tip.id.toString()),  // shows the ID inside a circle
  ),
  title: Text(tip.title),  // short title of the tip
  subtitle: Text(
    tip.description,   // small preview of the description
    maxLines: 2,       // only show 2 lines
    overflow: TextOverflow.ellipsis, // add "..." if text is too long
  ),
  onTap: () {
    // when user taps the tile -> navigate to detail screen
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => LifestyleTipDetailScreen(tipId: tip.id),
      ),
    );
  },
),
          );
        },
      ),
    );
  }
}
