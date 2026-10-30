import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:akinator_frontend/core/config/api_config.dart';
import 'package:akinator_frontend/core/errors/app_error.dart';
import 'package:akinator_frontend/models/question.dart';
import 'package:akinator_frontend/models/character_guess.dart';

class GameRepository {
  final http.Client _client;
  final String _baseUrl;

  GameRepository({http.Client? client, String? baseUrl})
      : _client = client ?? http.Client(),
        _baseUrl = baseUrl ?? ApiConfig.baseUrl;

  Future<Map<String, dynamic>> startGame() async {
    try {
      final response = await _client.post(
        Uri.parse('$_baseUrl/start-game'),
        headers: {'Content-Type': 'application/json; charset=utf-8'},
      );

      final body = jsonDecode(utf8.decode(response.bodyBytes));
      if (response.statusCode == 201) {
        return {
          'session_id': body['session_id'],
          'status': body['status'],
          'question': Question.fromJson(body['question']),
        };
      }
      throw _parseError(response.statusCode, body);
    } catch (e) {
      if (e is AppError) rethrow;
      throw NetworkError();
    }
  }

  Future<Map<String, dynamic>> submitAnswer(
    String sessionId,
    String questionCode,
    String answer,
  ) async {
    try {
      final response = await _client.post(
        Uri.parse('$_baseUrl/answer'),
        headers: {'Content-Type': 'application/json; charset=utf-8'},
        body: jsonEncode({
          'session_id': sessionId,
          'question_code': questionCode,
          'answer': answer,
        }),
      );

      final body = jsonDecode(utf8.decode(response.bodyBytes));
      if (response.statusCode == 200) {
        return {
          'status': body['status'],
          'next_question': body['next_question'] != null
              ? Question.fromJson(body['next_question'])
              : null,
          'guess': body['guess'] != null
              ? CharacterGuess.fromJson(body['guess'])
              : null,
        };
      }
      throw _parseError(response.statusCode, body);
    } catch (e) {
      if (e is AppError) rethrow;
      throw NetworkError();
    }
  }

  Future<Map<String, dynamic>> submitFeedback(
    String sessionId,
    String feedback,
  ) async {
    try {
      final response = await _client.post(
        Uri.parse('$_baseUrl/guess-feedback'),
        headers: {'Content-Type': 'application/json; charset=utf-8'},
        body: jsonEncode({
          'session_id': sessionId,
          'feedback': feedback,
        }),
      );

      final body = jsonDecode(utf8.decode(response.bodyBytes));
      if (response.statusCode == 200) {
        return {
          'status': body['status'],
          'message_bn': body['message_bn'],
          'next_question': body['next_question'] != null
              ? Question.fromJson(body['next_question'])
              : null,
          'guess': body['guess'] != null
              ? CharacterGuess.fromJson(body['guess'])
              : null,
        };
      }
      throw _parseError(response.statusCode, body);
    } catch (e) {
      if (e is AppError) rethrow;
      throw NetworkError();
    }
  }

  Future<Map<String, dynamic>> submitContribution(
    String sessionId,
    String nameBn,
    List<String> categories,
  ) async {
    try {
      final response = await _client.post(
        Uri.parse('$_baseUrl/contributions'),
        headers: {'Content-Type': 'application/json; charset=utf-8'},
        body: jsonEncode({
          'session_id': sessionId,
          'name_bn': nameBn,
          'categories': categories,
        }),
      );

      final body = jsonDecode(utf8.decode(response.bodyBytes));
      if (response.statusCode == 201) {
        return {
          'status': body['status'],
          'contribution_id': body['contribution_id'],
          'message_bn': body['message_bn'],
        };
      }
      throw _parseError(response.statusCode, body);
    } catch (e) {
      if (e is AppError) rethrow;
      throw NetworkError();
    }
  }

  AppError _parseError(int statusCode, Map<String, dynamic> body) {
    if (statusCode == 404 && body['error_code'] == 'SESSION_NOT_FOUND') {
      return SessionExpiredError();
    }
    return AppError(
      message: body['message'] ?? 'An error occurred',
      messageBn: body['message_bn'] ?? 'একটি সমস্যা দেখা দিয়েছে।',
      errorCode: body['error_code'],
      statusCode: statusCode,
    );
  }
}
