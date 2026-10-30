import 'package:flutter/material.dart';
import 'package:akinator_frontend/models/game_state.dart';
import 'package:akinator_frontend/core/theme/app_theme.dart';

class GenieAvatar extends StatelessWidget {
  final GameState status;
  final double size;

  const GenieAvatar({
    super.key,
    required this.status,
    this.size = 120,
  });

  String _getEmojiForState() {
    switch (status) {
      case GameState.guessPending:
        return '🧞‍♂️✨';
      case GameState.won:
        return '👑🧞‍♂️';
      case GameState.defeated:
        return '😲🧞‍♂️';
      case GameState.submittingAnswer:
      case GameState.submittingFeedback:
      case GameState.submittingContribution:
        return '🤔💭';
      case GameState.initial:
      case GameState.starting:
      case GameState.asking:
      default:
        return '🧞‍♂️';
    }
  }

  String _getSubtitleForState() {
    switch (status) {
      case GameState.guessPending:
        return 'আমি ধরে ফেলেছি!';
      case GameState.won:
        return 'জ্বিন অপ্রতিরোধ্য!';
      case GameState.defeated:
        return 'অবিশ্বাস্য! আপনি জিতেছেন!';
      case GameState.submittingAnswer:
      case GameState.submittingFeedback:
        return 'জ্বিন চিন্তা করছে...';
      default:
        return 'মনের মানুষের কথা ভাবুন...';
    }
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        Container(
          width: size,
          height: size,
          decoration: BoxDecoration(
            shape: BoxShape.circle,
            gradient: RadialGradient(
              colors: [
                AppTheme.accentPurple.withAlpha(200),
                AppTheme.surfaceDark,
              ],
            ),
            boxShadow: [
              BoxShadow(
                color: AppTheme.accentPurple.withAlpha(100),
                blurRadius: 24,
                spreadRadius: 4,
              ),
            ],
            border: Border.all(
              color: AppTheme.accentGold.withAlpha(150),
              width: 2,
            ),
          ),
          child: Center(
            child: Text(
              _getEmojiForState(),
              style: TextStyle(fontSize: size * 0.45),
            ),
          ),
        ),
        const SizedBox(height: 12),
        Text(
          _getSubtitleForState(),
          style: const TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.w500,
            color: AppTheme.accentGold,
          ),
        ),
      ],
    );
  }
}
