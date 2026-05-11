import importlib.util
from pathlib import Path


def load_ui_module():
    spec = importlib.util.spec_from_file_location(
        "trading_agents_ui",
        Path("期货TradingAgents系统_专业完整版界面.py"),
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class FakeResponse:
    def __init__(self, status_code, text=""):
        self.status_code = status_code
        self.text = text


def test_expired_deepseek_key_is_invalid():
    module = load_ui_module()

    def fake_post(url, headers=None, json=None, timeout=None):
        return FakeResponse(401, '{"error":{"message":"Authentication failed"}}')

    result = module.validate_deepseek_api_key(
        "sk-expired",
        "https://api.deepseek.com/v1",
        "deepseek-chat",
        http_post=fake_post,
    )

    assert result["status"] == "invalid"
    assert "DeepSeek" in result["message"]


def test_expired_serper_key_is_invalid():
    module = load_ui_module()

    def fake_post(url, headers=None, json=None, timeout=None):
        return FakeResponse(403, "Forbidden")

    result = module.validate_serper_api_key(
        "expired-serper-key",
        "https://google.serper.dev/search",
        http_post=fake_post,
    )

    assert result["status"] == "invalid"
    assert "Serper" in result["message"]


def test_serper_no_credits_is_invalid():
    module = load_ui_module()

    def fake_post(url, headers=None, json=None, timeout=None):
        return FakeResponse(400, '{"message":"Not enough credits","statusCode":400}')

    result = module.validate_serper_api_key(
        "valid-format-but-no-credits",
        "https://google.serper.dev/search",
        http_post=fake_post,
    )

    assert result["status"] == "invalid"
    assert "Serper" in result["message"]


def test_expired_bocha_key_is_invalid():
    module = load_ui_module()

    def fake_post(url, headers=None, json=None, timeout=None):
        return FakeResponse(401, '{"message":"Unauthorized"}')

    result = module.validate_bocha_api_key(
        "expired-bocha-key",
        "https://api.bochaai.com/v1/web-search",
        http_post=fake_post,
    )

    assert result["status"] == "invalid"
    assert "博查" in result["message"]


def test_bocha_validation_uses_bearer_auth_and_query_payload():
    module = load_ui_module()
    captured = {}

    def fake_post(url, headers=None, json=None, timeout=None):
        captured["url"] = url
        captured["headers"] = headers
        captured["json"] = json
        return FakeResponse(200, "{}")

    result = module.validate_bocha_api_key(
        "bocha-key",
        "https://api.bochaai.com/v1/web-search",
        http_post=fake_post,
    )

    assert result["status"] == "valid"
    assert captured["url"] == "https://api.bochaai.com/v1/web-search"
    assert captured["headers"]["Authorization"] == "Bearer bocha-key"
    assert captured["json"]["query"]
    assert captured["json"]["count"] == 1


if __name__ == "__main__":
    test_expired_deepseek_key_is_invalid()
    test_expired_serper_key_is_invalid()
    test_serper_no_credits_is_invalid()
    test_expired_bocha_key_is_invalid()
    test_bocha_validation_uses_bearer_auth_and_query_payload()
    print("api status validation tests passed")
