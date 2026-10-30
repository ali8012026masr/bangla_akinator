import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

class AppTheme {
  static const Color primaryDark = Color(0xFF1A0B2E);
  static const Color surfaceDark = Color(0xFF261245);
  static const Color accentGold = Color(0xFFFFD166);
  static const Color accentCyan = Color(0xFF06D6A0);
  static const Color accentPurple = Color(0xFF8338EC);

  static ThemeData get darkTheme {
    return ThemeData(
      brightness: Brightness.dark,
      scaffoldBackgroundColor: primaryDark,
      fontFamily: GoogleFonts.hindSiliguri().fontFamily,
      colorScheme: const ColorScheme.dark(
        primary: accentPurple,
        secondary: accentGold,
        surface: surfaceDark,
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(16),
          ),
        ),
      ),
    );
  }
}
