"""Unit tests for configuration validation."""

from app.core.config import Settings


def test_settings_defaults():
    s = Settings()
    assert s.DB_NAME == "bangla_akinator"
    assert s.MAX_QUESTIONS == 20
    assert s.MIN_QUESTIONS_BEFORE_GUESS == 3
    assert s.GUESS_SCORE_THRESHOLD == 0.75
    assert isinstance(s.CORS_ORIGINS, list)
    assert len(s.CORS_ORIGINS) > 0


def test_cors_origins_parsing():
    s1 = Settings(CORS_ORIGINS='["http://localhost:3000", "http://example.com"]')
    assert "http://localhost:3000" in s1.CORS_ORIGINS
    assert "http://example.com" in s1.CORS_ORIGINS

    s2 = Settings(CORS_ORIGINS="http://foo.com, http://bar.com")
    assert "http://foo.com" in s2.CORS_ORIGINS
    assert "http://bar.com" in s2.CORS_ORIGINS
