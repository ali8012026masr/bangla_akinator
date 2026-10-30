import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:akinator_frontend/providers/game_provider.dart';
import 'package:akinator_frontend/widgets/genie_avatar.dart';
import 'package:akinator_frontend/core/theme/app_theme.dart';
import 'package:akinator_frontend/models/game_state.dart';

class DefeatScreen extends ConsumerStatefulWidget {
  const DefeatScreen({super.key});

  @override
  ConsumerState<DefeatScreen> createState() => _DefeatScreenState();
}

class _DefeatScreenState extends ConsumerState<DefeatScreen> {
  final _formKey = GlobalKey<FormState>();
  final _nameController = TextEditingController();
  final _categoryController = TextEditingController();

  @override
  void dispose() {
    _nameController.dispose();
    _categoryController.dispose();
    super.dispose();
  }

  void _submit() {
    if (_formKey.currentState?.validate() ?? false) {
      final categories = _categoryController.text
          .split(',')
          .map((e) => e.trim())
          .where((e) => e.isNotEmpty)
          .toList();

      ref.read(gameStateProvider.notifier).submitMissingCharacter(
            _nameController.text.trim(),
            categories.isEmpty ? ['অন্যান্য'] : categories,
          );
    }
  }

  @override
  Widget build(BuildContext context) {
    final gameState = ref.watch(gameStateProvider);

    return Scaffold(
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        title: const Text('জ্বিনের পরাজয়!'),
        centerTitle: true,
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.symmetric(horizontal: 24.0, vertical: 16.0),
          child: Form(
            key: _formKey,
            child: Column(
              children: [
                const GenieAvatar(
                  status: GameState.defeated,
                  size: 100,
                ),
                const SizedBox(height: 20),
                const Text(
                  'অভিনন্দন! আপনি জ্বিনকে হারিয়েছেন! 🏆',
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    fontSize: 24,
                    fontWeight: FontWeight.bold,
                    color: AppTheme.accentGold,
                  ),
                ),
                const SizedBox(height: 10),
                const Text(
                  'জ্বিন আপনার মনের মানুষটিকে অনুমান করতে পারেনি। আপনি কার কথা ভাবছিলেন? নামটি শিখিয়ে দিন যাতে পরবর্তীতে জ্বিন আরও দক্ষ হতে পারে:',
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    fontSize: 15,
                    color: Colors.white70,
                    height: 1.4,
                  ),
                ),
                const SizedBox(height: 28),
                TextFormField(
                  controller: _nameController,
                  decoration: InputDecoration(
                    labelText: 'চরিত্রের নাম (বাংলায়)',
                    hintText: 'যেমন: তাসকিন আহমেদ',
                    prefixIcon: const Icon(Icons.person_rounded, color: AppTheme.accentGold),
                    filled: true,
                    fillColor: AppTheme.surfaceDark,
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(16),
                      borderSide: BorderSide.none,
                    ),
                    focusedBorder: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(16),
                      borderSide: const BorderSide(color: AppTheme.accentGold, width: 1.5),
                    ),
                  ),
                  validator: (val) {
                    if (val == null || val.trim().length < 2) {
                      return 'দয়া করে সঠিক নাম প্রদান করুন (কমপক্ষে ২ অক্ষর)';
                    }
                    return null;
                  },
                ),
                const SizedBox(height: 16),
                TextFormField(
                  controller: _categoryController,
                  decoration: InputDecoration(
                    labelText: 'ক্যাটাগরি বা পেশা (কমা দিয়ে একাধিক)',
                    hintText: 'যেমন: ক্রিকেটার, ক্রীড়াবিদ',
                    prefixIcon: const Icon(Icons.category_rounded, color: AppTheme.accentPurple),
                    filled: true,
                    fillColor: AppTheme.surfaceDark,
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(16),
                      borderSide: BorderSide.none,
                    ),
                    focusedBorder: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(16),
                      borderSide: const BorderSide(color: AppTheme.accentPurple, width: 1.5),
                    ),
                  ),
                ),
                const SizedBox(height: 32),
                if (gameState.isLoading)
                  const CircularProgressIndicator(color: AppTheme.accentGold)
                else
                  Column(
                    children: [
                      SizedBox(
                        width: double.infinity,
                        height: 54,
                        child: ElevatedButton.icon(
                          style: ElevatedButton.styleFrom(
                            backgroundColor: AppTheme.accentGold,
                            foregroundColor: AppTheme.primaryDark,
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(16),
                            ),
                          ),
                          onPressed: _submit,
                          icon: const Icon(Icons.send_rounded),
                          label: const Text(
                            'জ্বিনকে শিখিয়ে দিন',
                            style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                          ),
                        ),
                      ),
                      const SizedBox(height: 12),
                      TextButton(
                        onPressed: () => ref.read(gameStateProvider.notifier).resetGame(),
                        child: const Text(
                          'ছেড়ে দিন ও নতুন খেলা শুরু করুন',
                          style: TextStyle(color: Colors.white60, fontSize: 16),
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
