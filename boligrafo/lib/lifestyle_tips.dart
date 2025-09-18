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
    child: Text(tip.id.toString()),  
  ),
  title: Text(tip.title),  
  subtitle: Text(
    tip.description,   
    maxLines: 10,       
    overflow: TextOverflow.ellipsis, 
  ),
  onTap: () {
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
