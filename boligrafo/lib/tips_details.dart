import 'package:flutter/material.dart';
import 'tips_data.dart';  

class LifestyleTipDetailScreen extends StatelessWidget {
  final int tipId;

  const LifestyleTipDetailScreen({super.key, required this.tipId});

  @override
  Widget build(BuildContext context) {
    final tip = lifestyleTips.firstWhere((t) => t.id == tipId);

    return Scaffold(
      backgroundColor: Colors.grey[50],
      appBar: AppBar(
        title: Text(
          'Tip $tipId',
          style: const TextStyle(
            fontWeight: FontWeight.bold,
            color: Colors.white,
          ),
        ),
        centerTitle: true,
        elevation: 0,
        backgroundColor: _getTipColor(tipId),
        iconTheme: const IconThemeData(color: Colors.white),
        actions: [
          IconButton(
            icon: const Icon(Icons.share),
            onPressed: () {
              // Add share functionality
            },
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header Card
            Container(
              padding: const EdgeInsets.all(24),
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                  colors: [
                    _getTipColor(tipId),
                    _getTipColor(tipId).withOpacity(0.8),
                  ],
                ),
                borderRadius: BorderRadius.circular(20),
                boxShadow: [
                  BoxShadow(
                    color: _getTipColor(tipId).withOpacity(0.3),
                    blurRadius: 15,
                    offset: const Offset(0, 6),
                  ),
                ],
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.center,
                children: [
                  Container(
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: Colors.white.withOpacity(0.2),
                      shape: BoxShape.circle,
                    ),
                    child: Icon(
                      _getTipIcon(tipId),
                      size: 32,
                      color: Colors.white,
                    ),
                  ),
                  const SizedBox(height: 16),
                  Text(
                    tip.title,
                    style: const TextStyle(
                      fontSize: 24,
                      fontWeight: FontWeight.bold,
                      color: Colors.white,
                      height: 1.3,
                    ),
                    textAlign: TextAlign.center,
                  ),
                ],
              ),
            ),

            const SizedBox(height: 24),

            // Content Section
            Container(
              padding: const EdgeInsets.all(24),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(20),
                boxShadow: [
                  BoxShadow(
                    color: Colors.grey.withOpacity(0.1),
                    blurRadius: 10,
                    offset: const Offset(0, 4),
                  ),
                ],
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Section Header
                  Row(
                    children: [
                      Container(
                        padding: const EdgeInsets.all(6),
                        decoration: BoxDecoration(
                          color: _getTipColor(tipId).withOpacity(0.1),
                          shape: BoxShape.circle,
                        ),
                        child: Icon(
                          Icons.description,
                          size: 20,
                          color: _getTipColor(tipId),
                        ),
                      ),
                      const SizedBox(width: 12),
                      Text(
                        'Detailed Guidance',
                        style: TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                          color: _getTipColor(tipId),
                        ),
                      ),
                    ],
                  ),

                  const SizedBox(height: 16),

                  // Description
                  Text(
                    tip.description,
                    style: TextStyle(
                      fontSize: 16,
                      color: Colors.grey[700],
                      height: 1.6,
                    ),
                    textAlign: TextAlign.justify,
                  ),

                  const SizedBox(height: 24),

                  // Action Steps
                  _buildSection(
                    icon: Icons.check_circle,
                    title: 'Action Steps',
                    color: _getTipColor(tipId),
                    children: _getActionSteps(tipId),
                  ),

                  const SizedBox(height: 24),

                  // Benefits
                  _buildSection(
                    icon: Icons.thumb_up,
                    title: 'Key Benefits',
                    color: _getTipColor(tipId),
                    children: _getBenefits(tipId),
                  ),

                  const SizedBox(height: 24),

                  // Daily Challenge
                  Container(
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: _getTipColor(tipId).withOpacity(0.05),
                      borderRadius: BorderRadius.circular(16),
                      border: Border.all(
                        color: _getTipColor(tipId).withOpacity(0.2),
                      ),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            Icon(
                              Icons.emoji_events,
                              color: _getTipColor(tipId),
                              size: 20,
                            ),
                            const SizedBox(width: 8),
                            Text(
                              'Today\'s Challenge',
                              style: TextStyle(
                                fontWeight: FontWeight.bold,
                                color: _getTipColor(tipId),
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 8),
                        Text(
                          _getDailyChallenge(tipId),
                          style: TextStyle(
                            color: Colors.grey[700],
                            height: 1.4,
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),

            const SizedBox(height: 24),

            // Call to Action Button
            SizedBox(
              width: double.infinity,
              child: ElevatedButton.icon(
                onPressed: () {
                  // Add action functionality
                },
                icon: Icon(Icons.star, color: Colors.white),
                label: const Text(
                  'Start Implementing Today',
                  style: TextStyle(color: Colors.white),
                ),
                style: ElevatedButton.styleFrom(
                  backgroundColor: _getTipColor(tipId),
                  padding: const EdgeInsets.symmetric(vertical: 16),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                  elevation: 2,
                ),
              ),
            ),

            const SizedBox(height: 32),
          ],
        ),
      ),
    );
  }

  Widget _buildSection({
    required IconData icon,
    required String title,
    required Color color,
    required List<String> children,
  }) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Container(
              padding: const EdgeInsets.all(6),
              decoration: BoxDecoration(
                color: color.withOpacity(0.1),
                shape: BoxShape.circle,
              ),
              child: Icon(icon, size: 20, color: color),
            ),
            const SizedBox(width: 12),
            Text(
              title,
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
                color: color,
              ),
            ),
          ],
        ),
        const SizedBox(height: 12),
        ...children.map((item) => Padding(
          padding: const EdgeInsets.symmetric(vertical: 6),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Icon(
                Icons.circle,
                size: 8,
                color: color,
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Text(
                  item,
                  style: TextStyle(
                    color: Colors.grey[700],
                    height: 1.4,
                  ),
                ),
              ),
            ],
          ),
        )),
      ],
    );
  }

  Color _getTipColor(int id) {
    final colors = [
      Colors.green,
      Colors.blue,
      Colors.orange,
      Colors.purple,
      Colors.teal,
      Colors.pink,
      Colors.indigo,
      Colors.cyan,
      Colors.lime,
      Colors.amber,
    ];
    return colors[id % colors.length];
  }

  IconData _getTipIcon(int id) {
    final icons = [
      Icons.local_drink,
      Icons.directions_run,
      Icons.nightlight,
      Icons.restaurant,
      Icons.self_improvement,
      Icons.fastfood,
      Icons.people,
      Icons.psychology,
      Icons.emoji_emotions,
      Icons.air,
    ];
    return icons[id % icons.length];
  }

  List<String> _getActionSteps(int tipId) {
    final steps = {
      1: [
        'Carry a water bottle with you throughout the day',
        'Set hourly reminders to take water breaks',
        'Start and end your day with a glass of water',
        'Add lemon or mint for better flavor'
      ],
      2: [
        'Schedule 30 minutes for physical activity',
        'Choose activities you enjoy',
        'Use a fitness tracker to monitor progress',
        'Start with light exercises and gradually increase intensity'
      ],
      3: [
        'Establish a consistent sleep schedule',
        'Create a relaxing bedtime routine',
        'Keep your bedroom dark, quiet, and cool',
        'Avoid screens 1 hour before bedtime'
      ],
      // Add more for other tips...
    };
    return steps[tipId] ?? [
      'Set a specific time for this activity',
      'Track your progress daily',
      'Share your goals with a friend for accountability'
    ];
  }

  List<String> _getBenefits(int tipId) {
    final benefits = {
      1: [
        'Improved digestion and nutrient absorption',
        'Better skin health and complexion',
        'Regulated body temperature',
        'Enhanced detoxification processes'
      ],
      2: [
        'Lower blood pressure and improved heart health',
        'Increased energy levels throughout the day',
        'Better mood and reduced stress',
        'Weight management support'
      ],
      3: [
        'Enhanced memory and cognitive function',
        'Stronger immune system',
        'Better mood regulation',
        'Improved physical recovery'
      ],
      // Add more for other tips...
    };
    return benefits[tipId] ?? [
      'Improved overall health and wellbeing',
      'Better quality of life',
      'Reduced risk of chronic diseases',
      'Increased daily energy and vitality'
    ];
  }

  String _getDailyChallenge(int tipId) {
    final challenges = {
      1: 'Drink 8 glasses of water today. Track each glass with a checkmark!',
      2: 'Take a 30-minute walk after dinner. Invite a friend or family member!',
      3: 'Go to bed 30 minutes earlier tonight. Create a relaxing pre-sleep routine.',
      // Add more for other tips...
    };
    return challenges[tipId] ?? 'Practice this tip for at least 15 minutes today. You can do it!';
  }
}