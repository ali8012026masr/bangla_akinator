import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:akinator_frontend/providers/game_provider.dart';
import 'package:akinator_frontend/widgets/genie_avatar.dart';
import 'package:akinator_frontend/core/theme/app_theme.dart';
import 'package:akinator_frontend/models/game_state.dart';

class GameResultScreen extends ConsumerWidget {
  const GameResultScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final gameState = ref.watch(gameStateProvider);

    return Scaffold(
      body: SafeArea(
        child: Center(
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 28.0),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                const GenieAvatar(
                  status: GameState.won,
                  size: 130,
                ),
                const SizedBox(height: 28),
                Text(
                  gameState.winMessage ?? 'জ্বিনের মহাবিজয়! 🧞‍♂️',
                  textAlign: TextAlign.center,
                  style: const TextStyle(
                    fontSize: 28,
                    fontWeight: FontWeight.bold,
                    color: AppTheme.accentGold,
                    height: 1.3,
                  ),
                ),
                const SizedBox(height: 16),
                Container(
                  padding: const EdgeInsets.all(20),
                  decoration: BoxDecoration(
                    color: AppTheme.surfaceDark,
                    borderRadius: BorderRadius.circular(16),
                    border: Border.all(
                      color: AppTheme.accentPurple.withAlpha(120),
                    ),
                  ),
                  child: const Text(
                    'জ্বিন আবার প্রমাণ করল তার অলৌকিক জ্ঞান! আপনার মনের কথা গোপন রাখতে পারলেন না!',
                    textAlign: TextAlign.center,
                    style: TextStyle(
                      fontSize: 16,
                      color: Colors.white70,
                      height: 1.5,
                    ),
                  ),
                ),
                const SizedBox(height: 48),
                SizedBox(
                  width: double.infinity,
                  height: 56,
                  child: ElevatedButton(
                    style: ElevatedButton.styleFrom(
                      backgroundColor: AppTheme.accentGold,
                      foregroundColor: AppTheme.primaryDark,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(16),
                      ),
                    ),
                    onPressed: () => ref.read(gameStateProvider.notifier).resetGame(),
                    child: const Text(
                      'আবার নতুন করে খেলুন',
                      style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
