class Question {
  final String questionCode;
  final String textBn;
  final int questionNumber;

  const Question({
    required this.questionCode,
    required this.textBn,
    required this.questionNumber,
  });

  factory Question.fromJson(Map<String, dynamic> json) {
    return Question(
      questionCode: json['question_code'] as String,
      textBn: json['text_bn'] as String,
      questionNumber: json['question_number'] as int? ?? 1,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'question_code': questionCode,
      'text_bn': textBn,
      'question_number': questionNumber,
    };
  }
}
