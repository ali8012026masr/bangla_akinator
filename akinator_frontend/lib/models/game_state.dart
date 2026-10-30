import 'package:akinator_frontend/models/question.dart';
import 'package:akinator_frontend/models/character_guess.dart';

enum GameState {
  initial,
  starting,
  asking,
  submittingAnswer,
  guessPending,
  submittingFeedback,
  won,
  defeated,
  submittingContribution,
  contributionSent,
  error,
}

class GameSessionState {
  final GameState status;
  final String? sessionId;
  final Question? currentQuestion;
  final CharacterGuess? guess;
  final String? winMessage;
  final String? contributionMessage;
  final String? errorMessage;
  final int questionNumber;

  const GameSessionState({
    this.status = GameState.initial,
    this.sessionId,
    this.currentQuestion,
    this.guess,
    this.winMessage,
    this.contributionMessage,
    this.errorMessage,
    this.questionNumber = 0,
  });

  bool get isLoading =>
      status == GameState.starting ||
      status == GameState.submittingAnswer ||
      status == GameState.submittingFeedback ||
      status == GameState.submittingContribution;

  GameSessionState copyWith({
    GameState? status,
    String? sessionId,
    Question? currentQuestion,
    CharacterGuess? guess,
    String? winMessage,
    String? contributionMessage,
    String? errorMessage,
    int? questionNumber,
  }) {
    return GameSessionState(
      status: status ?? this.status,
      sessionId: sessionId ?? this.sessionId,
      currentQuestion: currentQuestion ?? this.currentQuestion,
      guess: guess ?? this.guess,
      winMessage: winMessage ?? this.winMessage,
      contributionMessage: contributionMessage ?? this.contributionMessage,
      errorMessage: errorMessage ?? this.errorMessage,
      questionNumber: questionNumber ?? this.questionNumber,
    );
  }
}
