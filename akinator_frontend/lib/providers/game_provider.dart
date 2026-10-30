import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_riverpod/legacy.dart';
import 'package:akinator_frontend/models/game_state.dart';
import 'package:akinator_frontend/repositories/game_repository.dart';
import 'package:akinator_frontend/core/errors/app_error.dart';

final gameRepositoryProvider = Provider<GameRepository>((ref) {
  return GameRepository();
});

final gameStateProvider =
    StateNotifierProvider<GameNotifier, GameSessionState>((ref) {
  final repo = ref.watch(gameRepositoryProvider);
  return GameNotifier(repo);
});

class GameNotifier extends StateNotifier<GameSessionState> {
  final GameRepository _repository;

  GameNotifier(this._repository) : super(const GameSessionState());

  Future<void> startNewGame() async {
    state = state.copyWith(
      status: GameState.starting,
      errorMessage: null,
    );

    try {
      final res = await _repository.startGame();
      state = GameSessionState(
        status: GameState.asking,
        sessionId: res['session_id'],
        currentQuestion: res['question'],
        questionNumber: 1,
      );
    } catch (e) {
      _handleError(e);
    }
  }

  Future<void> sendAnswer(String answerEnum) async {
    final session = state.sessionId;
    final currentQ = state.currentQuestion;
    if (session == null || currentQ == null || state.isLoading) return;

    state = state.copyWith(status: GameState.submittingAnswer);

    try {
      final res = await _repository.submitAnswer(
        session,
        currentQ.questionCode,
        answerEnum,
      );

      final statusStr = res['status'] as String;

      if (statusStr == 'guess_pending') {
        state = state.copyWith(
          status: GameState.guessPending,
          guess: res['guess'],
        );
      } else if (statusStr == 'defeated') {
        state = state.copyWith(
          status: GameState.defeated,
        );
      } else {
        state = state.copyWith(
          status: GameState.asking,
          currentQuestion: res['next_question'],
          questionNumber: state.questionNumber + 1,
        );
      }
    } catch (e) {
      _handleError(e);
    }
  }

  Future<void> submitGuessFeedback(bool isCorrect) async {
    final session = state.sessionId;
    if (session == null || state.isLoading) return;

    state = state.copyWith(status: GameState.submittingFeedback);

    try {
      final feedbackStr = isCorrect ? 'correct' : 'wrong';
      final res = await _repository.submitFeedback(session, feedbackStr);
      final statusStr = res['status'] as String;

      if (statusStr == 'won') {
        state = state.copyWith(
          status: GameState.won,
          winMessage: res['message_bn'],
        );
      } else if (statusStr == 'defeated') {
        state = state.copyWith(
          status: GameState.defeated,
        );
      } else {
        state = state.copyWith(
          status: GameState.asking,
          currentQuestion: res['next_question'],
          guess: null,
          questionNumber: state.questionNumber + 1,
        );
      }
    } catch (e) {
      _handleError(e);
    }
  }

  Future<void> submitMissingCharacter(
    String nameBn,
    List<String> categories,
  ) async {
    final session = state.sessionId;
    if (session == null || state.isLoading) return;

    state = state.copyWith(status: GameState.submittingContribution);

    try {
      final res = await _repository.submitContribution(
        session,
        nameBn,
        categories,
      );
      state = state.copyWith(
        status: GameState.contributionSent,
        contributionMessage: res['message_bn'],
      );
    } catch (e) {
      _handleError(e);
    }
  }

  void resetGame() {
    state = const GameSessionState();
  }

  void _handleError(Object error) {
    if (error is AppError) {
      state = state.copyWith(
        status: GameState.error,
        errorMessage: error.messageBn,
      );
    } else {
      state = state.copyWith(
        status: GameState.error,
        errorMessage: 'একটি অপ্রত্যাশিত ত্রুটি ঘটেছে। পুনরায় চেষ্টা করুন।',
      );
    }
  }
}
