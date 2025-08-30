class LifestyleTip {
  final int id;
  final String title;        
  final String description;  
  final String? imageUrl;
  final String? image; 


  const LifestyleTip({
    required this.id,
    required this.title,
    required this.description,
    this.imageUrl,
    this.image,
  });
}
