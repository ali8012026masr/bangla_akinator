import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:akinator_frontend/providers/game_provider.dart';
import 'package:akinator_frontend/widgets/genie_avatar.dart';
import 'package:akinator_frontend/widgets/answer_button.dart';
import 'package:akinator_frontend/core/theme/app_theme.dart';

class GameScreen extends ConsumerWidget {
  const GameScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final gameState = ref.watch(gameStateProvider);
    final question = gameState.currentQuestion;

    return Scaffold(
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        title: Text(
          'প্রশ্ন নং ${gameState.questionNumber}',
          style: const TextStyle(fontWeight: FontWeight.bold),
        ),
        centerTitle: true,
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh_rounded),
            tooltip: 'নতুন করে শুরু করুন',
            onPressed: () => ref.read(gameStateProvider.notifier).resetGame(),
          ),
        ],
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.symmetric(horizontal: 24.0, vertical: 12.0),
          child: Column(
            children: [
              GenieAvatar(
                status: gameState.status,
                size: 90,
              ),
              const SizedBox(height: 20),
              // Question Card
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(24),
                decoration: BoxDecoration(
                  color: AppTheme.surfaceDark,
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(
                    color: AppTheme.accentGold.withAlpha(120),
                    width: 1.5,
                  ),
                  boxShadow: [
                    BoxShadow(
                      color: AppTheme.accentGold.withAlpha(30),
                      blurRadius: 16,
                      offset: const Offset(0, 4),
                    ),
                  ],
                ),
                child: Text(
                  question?.textBn ?? 'প্রশ্ন আসছে...',
                  textAlign: TextAlign.center,
                  style: const TextStyle(
                    fontSize: 22,
                    fontWeight: FontWeight.w600,
                    height: 1.4,
                    color: Colors.white,
                  ),
                ),
              ),
              const SizedBox(height: 24),
              if (gameState.isLoading)
                const Padding(
                  padding: EdgeInsets.symmetric(vertical: 20.0),
                  child: CircularProgressIndicator(color: AppTheme.accentGold),
                )
              else
                Column(
                  children: [
                    AnswerButton(
                      label: 'হ্যাঁ (Yes)',
                      answerEnum: 'YES',
                      baseColor: const Color(0xFF06D6A0),
                      icon: Icons.check_circle_rounded,
                      isEnabled: !gameState.isLoading,
                      onPressed: () => ref
                          .read(gameStateProvider.notifier)
                          .sendAnswer('YES'),
                    ),
                    AnswerButton(
                      label: 'সম্ভবত হ্যাঁ (Probably Yes)',
                      answerEnum: 'PROBABLY_YES',
                      baseColor: const Color(0xFF118AB2),
                      icon: Icons.thumb_up_alt_rounded,
                      isEnabled: !gameState.isLoading,
                      onPressed: () => ref
                          .read(gameStateProvider.notifier)
                          .sendAnswer('PROBABLY_YES'),
                    ),
                    AnswerButton(
                      label: 'জানি না (Don\'t Know)',
                      answerEnum: 'UNKNOWN',
                      baseColor: const Color(0xFF8338EC),
                      icon: Icons.help_outline_rounded,
                      isEnabled: !gameState.isLoading,
                      onPressed: () => ref
                          .read(gameStateProvider.notifier)
                          .sendAnswer('UNKNOWN'),
                    ),
                    AnswerButton(
                      label: 'সম্ভবত না (Probably Not)',
                      answerEnum: 'PROBABLY_NO',
                      baseColor: const Color(0xFFFF9F1C),
                      icon: Icons.thumb_down_alt_rounded,
                      isEnabled: !gameState.isLoading,
                      onPressed: () => ref
                          .read(gameStateProvider.notifier)
                          .sendAnswer('PROBABLY_NO'),
                    ),
                    AnswerButton(
                      label: 'না (No)',
                      answerEnum: 'NO',
                      baseColor: const Color(0xFFEF476F),
                      icon: Icons.cancel_rounded,
                      isEnabled: !gameState.isLoading,
                      onPressed: () => ref
                          .read(gameStateProvider.notifier)
                          .sendAnswer('NO'),
                    ),
                  ],
                ),
            ],
          ),
        ),
      ),
    );
  }
}
