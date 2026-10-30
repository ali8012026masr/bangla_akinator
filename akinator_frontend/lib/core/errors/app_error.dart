class AppError implements Exception {
  final String message;
  final String messageBn;
  final String? errorCode;
  final int? statusCode;

  AppError({
    required this.message,
    required this.messageBn,
    this.errorCode,
    this.statusCode,
  });

  @override
  String toString() => 'AppError: $message ($errorCode)';
}

class NetworkError extends AppError {
  NetworkError()
      : super(
          message: 'Failed to communicate with server.',
          messageBn: 'সার্ভারের সাথে সংযোগ স্থাপন করা যায়নি। আপনার ইন্টারনেট অথবা ব্যাকএন্ড চালু আছে কি না পরীক্ষা করুন।',
          errorCode: 'NETWORK_ERROR',
        );
}

class SessionExpiredError extends AppError {
  SessionExpiredError()
      : super(
          message: 'The current game session has expired.',
          messageBn: 'খেলার সেশনের সময়সীমা শেষ হয়ে গেছে। দয়া করে নতুন খেলা শুরু করুন।',
          errorCode: 'SESSION_EXPIRED',
          statusCode: 404,
        );
}
