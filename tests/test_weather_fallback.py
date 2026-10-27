"""Unit tests for weather forecasting and offline fallback handling."""

from unittest.mock import patch
import pytest
from src.weather_service import get_weather_forecast


def test_live_or_fallback_structure():
    res = get_weather_forecast("IND_DEL_001")
    assert "is_live" in res
    assert "destination_name" in res
    assert "climate_summary" in res
    assert "source" in res
    assert "status_message" in res


def test_timeout_and_network_failure_fallback():
    from src.weather_service import _weather_cache
    _weather_cache.clear()
    # Simulate network error by patching requests.get to raise ConnectionError
    with patch("requests.get", side_effect=Exception("Simulated connection timeout")):
        res = get_weather_forecast("IND_DEL_001")
        assert res["is_live"] is False
        assert "Offline Fallback" in res["source"]
        assert "climate_summary" in res
        assert len(res["climate_summary"]) > 5


def test_invalid_destination():
    res = get_weather_forecast("INVALID_ID_9999")
    assert res["is_live"] is False
    assert "Destination not found" in res["status_message"]
