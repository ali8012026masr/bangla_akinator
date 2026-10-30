import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:akinator_frontend/providers/game_provider.dart';
import 'package:akinator_frontend/core/theme/app_theme.dart';

class ContributionStatusScreen extends ConsumerWidget {
  const ContributionStatusScreen({super.key});

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
                Container(
                  width: 100,
                  height: 100,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    color: const Color(0xFF06D6A0).withAlpha(40),
                    border: Border.all(color: const Color(0xFF06D6A0), width: 2),
                  ),
                  child: const Icon(
                    Icons.check_circle_outline_rounded,
                    color: Color(0xFF06D6A0),
                    size: 56,
                  ),
                ),
                const SizedBox(height: 24),
                const Text(
                  'ধন্যবাদ! প্রস্তাব জমা হয়েছে',
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    fontSize: 26,
                    fontWeight: FontWeight.bold,
                    color: AppTheme.accentGold,
                  ),
                ),
                const SizedBox(height: 16),
                Container(
                  padding: const EdgeInsets.all(20),
                  decoration: BoxDecoration(
                    color: AppTheme.surfaceDark,
                    borderRadius: BorderRadius.circular(16),
                  ),
                  child: Text(
                    gameState.contributionMessage ??
                        'আপনার প্রস্তাবটি সফলভাবে পর্যালোচনার জন্য জমা হয়েছে। অ্যাডমিন পর্যালোচনার পর এটি জ্বিনের সাধারণ জ্ঞানে যুক্ত হবে।',
                    textAlign: TextAlign.center,
                    style: const TextStyle(
                      fontSize: 16,
                      color: Colors.white70,
                      height: 1.5,
                    ),
                  ),
                ),
                const SizedBox(height: 40),
                SizedBox(
                  width: double.infinity,
                  height: 54,
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
                      'আবার খেলুন',
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
