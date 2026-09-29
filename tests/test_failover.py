from unittest.mock import MagicMock, patch

import pytest

from chatrelay import Chatbot, LLMError, build_providers


@pytest.fixture(autouse=True)
def keys(monkeypatch):
    monkeypatch.setenv("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,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", "g1,g2")
    monkeypatch.setenv("AQ.Ab8RN6L-hgvlDA1teDwOjMw7OljAbaD6ww30uyXSezTwY92alg,AQ.Ab8RN6KugZFooESpmD_WJnYr65Lun92pUPJ39T25qqig7AYxxQ.", "m1,m2")


def make_post(groq_status=200, gemini_status=200):
    def fake(url, headers=None, json=None, timeout=None):
        r = MagicMock(headers={})
        if "groq" in url:
            r.status_code = groq_status
            r.json.return_value = {"choices": [{"message": {"content": "hi from groq"}}]}
        else:
            r.status_code = gemini_status
            r.json.return_value = {"candidates": [{"content": {"parts": [{"text": "hi from gemini"}]}}]}
        return r
    return fake


def test_key_order():
    assert list(build_providers()) == ["groq-1", "groq-2", "gemini-1", "gemini-2"]


def test_uses_first_key_when_ok():
    with patch("requests.post", side_effect=make_post()):
        assert Chatbot(build_providers()).ask("x")["provider"] == "groq-1"


def test_falls_back_to_gemini_when_groq_limited_and_skips_next_time():
    bot = Chatbot(build_providers())
    with patch("requests.post", side_effect=make_post(groq_status=429)) as m:
        assert bot.ask("x")["provider"] == "gemini-1"
        before = m.call_count
        bot.ask("y")
        assert m.call_count - before == 1  # groq keys in cooldown, skipped


def test_all_fail():
    with patch("requests.post", side_effect=make_post(429, 429)):
        with pytest.raises(LLMError):
            Chatbot(build_providers()).ask("x")


def test_history_kept():
    bot = Chatbot(build_providers())
    with patch("requests.post", side_effect=make_post()):
        bot.ask("one"); bot.ask("two")
    assert len(bot.history) == 4


def test_unknown_provider():
    with pytest.raises(ValueError):
        Chatbot(build_providers()).ask("x", provider="nope")
