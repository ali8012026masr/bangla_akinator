import 'package:flutter/material.dart';

class AnswerButton extends StatelessWidget {
  final String label;
  final String answerEnum;
  final Color baseColor;
  final IconData icon;
  final bool isEnabled;
  final VoidCallback onPressed;

  const AnswerButton({
    super.key,
    required this.label,
    required this.answerEnum,
    required this.baseColor,
    required this.icon,
    required this.isEnabled,
    required this.onPressed,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 6.0),
      child: Material(
        color: isEnabled ? baseColor.withAlpha(45) : Colors.white10,
        borderRadius: BorderRadius.circular(16),
        child: InkWell(
          borderRadius: BorderRadius.circular(16),
          onTap: isEnabled ? onPressed : null,
          child: Container(
            constraints: const BoxConstraints(minHeight: 56),
            padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(16),
              border: Border.all(
                color: isEnabled ? baseColor.withAlpha(180) : Colors.white24,
                width: 1.5,
              ),
            ),
            child: Row(
              children: [
                Icon(
                  icon,
                  color: isEnabled ? baseColor : Colors.white38,
                  size: 24,
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Text(
                    label,
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.w600,
                      color: isEnabled ? Colors.white : Colors.white38,
                    ),
                  ),
                ),
                Icon(
                  Icons.arrow_forward_ios_rounded,
                  size: 16,
                  color: isEnabled ? Colors.white38 : Colors.transparent,
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
