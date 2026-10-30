import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:akinator_frontend/providers/game_provider.dart';
import 'package:akinator_frontend/widgets/genie_avatar.dart';
import 'package:akinator_frontend/core/theme/app_theme.dart';
import 'package:akinator_frontend/models/game_state.dart';

class GuessScreen extends ConsumerWidget {
  const GuessScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final gameState = ref.watch(gameStateProvider);
    final guess = gameState.guess;

    return Scaffold(
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        title: const Text('জ্বিনের অনুমান! 🧞‍♂️'),
        centerTitle: true,
      ),
      body: SafeArea(
        child: Center(
          child: SingleChildScrollView(
            padding: const EdgeInsets.symmetric(horizontal: 28.0, vertical: 20.0),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                const GenieAvatar(
                  status: GameState.guessPending,
                  size: 110,
                ),
                const SizedBox(height: 24),
                const Text(
                  'আপনি কি এঁর কথা ভাবছিলেন?',
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    fontSize: 20,
                    color: Colors.white70,
                  ),
                ),
                const SizedBox(height: 16),
                Container(
                  width: double.infinity,
                  padding: const EdgeInsets.all(24),
                  decoration: BoxDecoration(
                    color: AppTheme.surfaceDark,
                    borderRadius: BorderRadius.circular(20),
                    border: Border.all(
                      color: AppTheme.accentGold,
                      width: 2,
                    ),
                    boxShadow: [
                      BoxShadow(
                        color: AppTheme.accentGold.withAlpha(50),
                        blurRadius: 20,
                        spreadRadius: 2,
                      ),
                    ],
                  ),
                  child: Column(
                    children: [
                      Text(
                        guess?.nameBn ?? '',
                        textAlign: TextAlign.center,
                        style: const TextStyle(
                          fontSize: 32,
                          fontWeight: FontWeight.bold,
                          color: AppTheme.accentGold,
                        ),
                      ),
                      const SizedBox(height: 12),
                      Wrap(
                        spacing: 8,
                        runSpacing: 6,
                        alignment: WrapAlignment.center,
                        children: (guess?.categories ?? []).map((cat) {
                          return Chip(
                            backgroundColor: AppTheme.accentPurple.withAlpha(80),
                            label: Text(
                              cat,
                              style: const TextStyle(color: Colors.white, fontSize: 13),
                            ),
                            side: BorderSide(
                              color: AppTheme.accentPurple.withAlpha(150),
                            ),
                          );
                        }).toList(),
                      ),
                      const SizedBox(height: 16),
                      Text(
                        'মিলের মাত্রা: ${(guess?.score != null ? (guess!.score * 100).toStringAsFixed(0) : "0")}%',
                        style: TextStyle(
                          fontSize: 14,
                          color: Colors.white.withAlpha(160),
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 36),
                if (gameState.isLoading)
                  const CircularProgressIndicator(color: AppTheme.accentGold)
                else
                  Column(
                    children: [
                      SizedBox(
                        width: double.infinity,
                        height: 56,
                        child: ElevatedButton.icon(
                          style: ElevatedButton.styleFrom(
                            backgroundColor: const Color(0xFF06D6A0),
                            foregroundColor: Colors.black87,
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(16),
                            ),
                          ),
                          onPressed: () => ref
                              .read(gameStateProvider.notifier)
                              .submitGuessFeedback(true),
                          icon: const Icon(Icons.check_rounded, size: 28),
                          label: const Text(
                            'হ্যাঁ! সঠিক অনুমান!',
                            style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                          ),
                        ),
                      ),
                      const SizedBox(height: 14),
                      SizedBox(
                        width: double.infinity,
                        height: 56,
                        child: OutlinedButton.icon(
                          style: OutlinedButton.styleFrom(
                            foregroundColor: Colors.redAccent,
                            side: const BorderSide(color: Colors.redAccent, width: 1.5),
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(16),
                            ),
                          ),
                          onPressed: () => ref
                              .read(gameStateProvider.notifier)
                              .submitGuessFeedback(false),
                          icon: const Icon(Icons.close_rounded, size: 28),
                          label: const Text(
                            'না, ভুল অনুমান!',
                            style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                          ),
                        ),
                      ),
                    ],
                  ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
