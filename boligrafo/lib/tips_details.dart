import 'package:flutter/material.dart';
import 'tips_data.dart';  

class LifestyleTipDetailScreen extends StatelessWidget {
  final int tipId;   // receives the ID of the tip

  const LifestyleTipDetailScreen({super.key, required this.tipId});

  @override
  Widget build(BuildContext context) {
    // find the tip with the matching ID
    final tip = lifestyleTips.firstWhere((t) => t.id == tipId);

    return Scaffold(
      appBar: AppBar(
        title: Text(tip.title),   // show title in the AppBar
        backgroundColor: Colors.green,
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
        
            if (tip.imageUrl != null) 
              Center(
                child: Image.asset(
                  tip.imageUrl!,
                  height: 150,
                  fit: BoxFit.cover,
                ),
              ),

            const SizedBox(height: 16),

            // ✅ Title (big and bold)
            Text(
              tip.title,
              style: const TextStyle(fontSize: 22, fontWeight: FontWeight.bold),
            ),

            const SizedBox(height: 8),

            // ✅ Full description (paragraph)
            Text(
              tip.description,
              style: const TextStyle(fontSize: 16),
            ),
          ],
        ),
      ),
    );
  }
}

