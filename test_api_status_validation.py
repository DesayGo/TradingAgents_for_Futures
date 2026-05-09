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


if __name__ == "__main__":
    test_expired_deepseek_key_is_invalid()
    test_expired_serper_key_is_invalid()
    test_serper_no_credits_is_invalid()
    print("api status validation tests passed")
