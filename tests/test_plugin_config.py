from pathlib import Path

import pytest
import yaml

import importlib.util


def load_plugin():
    path = Path(__file__).resolve().parents[1] / "__init__.py"
    spec = importlib.util.spec_from_file_location("hermes_local_tts_test", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_configured_mode_fast(monkeypatch, tmp_path: Path) -> None:
    module = load_plugin()
    (tmp_path / "config.yaml").write_text(yaml.safe_dump({"tts": {"local_tts": {"mode": "fast"}}}))
    monkeypatch.setattr(module, "get_hermes_home", lambda: tmp_path)
    assert module._configured_mode() == "fast"


def test_configured_mode_quality(monkeypatch, tmp_path: Path) -> None:
    module = load_plugin()
    (tmp_path / "config.yaml").write_text(yaml.safe_dump({"tts": {"local_tts": {"mode": "quality"}}}))
    monkeypatch.setattr(module, "get_hermes_home", lambda: tmp_path)
    assert module._configured_mode() == "quality"


def test_configured_mode_rejects_unknown(monkeypatch, tmp_path: Path) -> None:
    module = load_plugin()
    (tmp_path / "config.yaml").write_text(yaml.safe_dump({"tts": {"local_tts": {"mode": "turbo"}}}))
    monkeypatch.setattr(module, "get_hermes_home", lambda: tmp_path)
    with pytest.raises(RuntimeError, match="must be 'fast' or 'quality'"):
        module._configured_mode()
