class CharacterGuess {
  final String characterId;
  final String nameBn;
  final List<String> categories;
  final String? imageUrl;
  final double score;

  const CharacterGuess({
    required this.characterId,
    required this.nameBn,
    required this.categories,
    this.imageUrl,
    required this.score,
  });

  factory CharacterGuess.fromJson(Map<String, dynamic> json) {
    return CharacterGuess(
      characterId: json['character_id'] as String,
      nameBn: json['name_bn'] as String,
      categories: (json['categories'] as List<dynamic>?)
              ?.map((e) => e.toString())
              .toList() ??
          [],
      imageUrl: json['image_url'] as String?,
      score: (json['score'] as num?)?.toDouble() ?? 0.0,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'character_id': characterId,
      'name_bn': nameBn,
      'categories': categories,
      'image_url': imageUrl,
      'score': score,
    };
  }
}
