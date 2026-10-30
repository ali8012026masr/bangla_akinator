import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:akinator_frontend/core/theme/app_theme.dart';
import 'package:akinator_frontend/providers/game_provider.dart';
import 'package:akinator_frontend/models/game_state.dart';
import 'package:akinator_frontend/screens/home_screen.dart';
import 'package:akinator_frontend/screens/game_screen.dart';
import 'package:akinator_frontend/screens/guess_screen.dart';
import 'package:akinator_frontend/screens/defeat_screen.dart';
import 'package:akinator_frontend/screens/contribution_status_screen.dart';
import 'package:akinator_frontend/screens/game_result_screen.dart';

class BanglaAkinatorApp extends StatelessWidget {
  const BanglaAkinatorApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'বাংলা জ্বিন (Bangla Akinator)',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.darkTheme,
      home: const MainGameNavigator(),
    );
  }
}

class MainGameNavigator extends ConsumerWidget {
  const MainGameNavigator({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(gameStateProvider);

    switch (state.status) {
      case GameState.won:
        return const GameResultScreen();
      case GameState.defeated:
      case GameState.submittingContribution:
        return const DefeatScreen();
      case GameState.contributionSent:
        return const ContributionStatusScreen();
      case GameState.guessPending:
      case GameState.submittingFeedback:
        return const GuessScreen();
      case GameState.asking:
      case GameState.submittingAnswer:
        return const GameScreen();
      case GameState.initial:
      case GameState.starting:
      case GameState.error:
        return const HomeScreen();
    }
  }
}
