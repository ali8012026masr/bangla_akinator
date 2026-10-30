import 'package:flutter/foundation.dart';

class ApiConfig {
  static const String _defaultOverride = String.fromEnvironment('API_BASE_URL');

  static String get baseUrl {
    if (_defaultOverride.isNotEmpty) {
      return _defaultOverride;
    }

    if (kIsWeb) {
      return 'http://127.0.0.1:8000/api';
    }

    switch (defaultTargetPlatform) {
      case TargetPlatform.android:
        // Android Emulator loops back to development host on 10.0.2.2
        return 'http://10.0.2.2:8000/api';
      case TargetPlatform.iOS:
      case TargetPlatform.macOS:
      case TargetPlatform.windows:
      case TargetPlatform.linux:
      default:
        return 'http://127.0.0.1:8000/api';
    }
  }
}
