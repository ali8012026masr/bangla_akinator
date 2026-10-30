import 'package:flutter_test/flutter_test.dart';
import 'package:akinator_frontend/models/game_state.dart';
import 'package:akinator_frontend/models/question.dart';
import 'package:akinator_frontend/models/character_guess.dart';

void main() {
  group('Game Models and State tests', () {
    test('Question JSON serialization', () {
      final json = {
        'question_code': 'q_cricketer',
        'text_bn': 'তিনি কি ক্রিকেটার?',
        'question_number': 3,
      };

      final q = Question.fromJson(json);
      expect(q.questionCode, 'q_cricketer');
      expect(q.textBn, 'তিনি কি ক্রিকেটার?');
      expect(q.questionNumber, 3);
      expect(q.toJson(), json);
    });

    test('CharacterGuess JSON serialization', () {
      final json = {
        'character_id': 'char_123',
        'name_bn': 'সাকিব আল হাসান',
        'categories': ['ক্রিকেটার', 'ক্রীড়াবিদ'],
        'image_url': null,
        'score': 0.88,
      };

      final g = CharacterGuess.fromJson(json);
      expect(g.characterId, 'char_123');
      expect(g.nameBn, 'সাকিব আল হাসান');
      expect(g.categories, ['ক্রিকেটার', 'ক্রীড়াবিদ']);
      expect(g.score, 0.88);
    });

    test('GameSessionState copyWith and loading status', () {
      const state = GameSessionState(status: GameState.initial);
      expect(state.isLoading, isFalse);

      final starting = state.copyWith(status: GameState.starting);
      expect(starting.isLoading, isTrue);

      final asking = starting.copyWith(status: GameState.asking, questionNumber: 1);
      expect(asking.isLoading, isFalse);
      expect(asking.questionNumber, 1);
    });
  });
}
