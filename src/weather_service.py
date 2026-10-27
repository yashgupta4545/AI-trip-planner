"""Weather service integrating Open-Meteo forecast API with TTL caching and offline climate fallback.
"""

import time
from typing import Any, Dict, Optional
import requests

from src.config import OPEN_METEO_BASE_URL, WEATHER_CACHE_TTL_SECONDS
from src.data_loader import get_destination_by_id

# WMO Weather Interpretation Codes
WMO_CODE_MAP = {
    0: ("Clear Sky", "☀️"),
    1: ("Mainly Clear", "🌤️"),
    2: ("Partly Cloudy", "⛅"),
    3: ("Overcast", "☁️"),
    45: ("Foggy", "🌫️"),
    48: ("Depositing Rime Fog", "🌫️"),
    51: ("Light Drizzle", "🌦️"),
    53: ("Moderate Drizzle", "🌦️"),
    55: ("Dense Drizzle", "🌧️"),
    61: ("Slight Rain", "🌧️"),
    63: ("Moderate Rain", "🌧️"),
    65: ("Heavy Rain", "🌧️"),
    71: ("Slight Snow", "🌨️"),
    73: ("Moderate Snow", "🌨️"),
    75: ("Heavy Snow", "❄️"),
    80: ("Slight Rain Showers", "🌦️"),
    81: ("Moderate Showers", "🌧️"),
    82: ("Violent Showers", "⛈️"),
    95: ("Thunderstorm", "⛈️"),
    96: ("Thunderstorm with Slight Hail", "⛈️"),
    99: ("Thunderstorm with Heavy Hail", "⛈️"),
}

# In-memory weather cache: key -> (timestamp, data)
_weather_cache: Dict[str, tuple] = {}


def get_weather_forecast(destination_id: str, timeout_seconds: float = 4.0) -> Dict[str, Any]:
    """Retrieve live weather forecast from Open-Meteo or fall back gracefully to climate summary."""
    dest = get_destination_by_id(destination_id)
    if not dest:
        return _build_error_fallback("Destination not found.")

    lat = dest.get("latitude")
    lon = dest.get("longitude")
    dest_name = dest.get("destination_name", "Destination")
    climate_summary = dest.get("climate_summary", "Pleasant seasonal conditions.")
    best_season = dest.get("best_season", "All year")

    # Coordinate check
    if lat is None or lon is None or not (-90.0 <= lat <= 90.0) or not (-180.0 <= lon <= 180.0):
        return {
            "is_live": False,
            "destination_name": dest_name,
            "source": "Historical Climate Summary",
            "status_message": "Geographic coordinates unavailable for live forecast. Displaying curated climate data.",
            "climate_summary": climate_summary,
            "best_season": best_season,
            "daily_forecast": []
        }

    # Check Cache
    cache_key = f"{round(lat, 2)}_{round(lon, 2)}"
    now = time.time()
    if cache_key in _weather_cache:
        cached_time, cached_data = _weather_cache[cache_key]
        if now - cached_time < WEATHER_CACHE_TTL_SECONDS:
            return cached_data

    # Request Open-Meteo API
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,weather_code,wind_speed_10m",
        "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum",
        "timezone": "auto"
    }

    try:
        resp = requests.get(OPEN_METEO_BASE_URL, params=params, timeout=timeout_seconds)
        if resp.status_code == 200:
            data = resp.json()
            curr = data.get("current", {})
            daily = data.get("daily", {})

            w_code = curr.get("weather_code", 0)
            condition_desc, icon = WMO_CODE_MAP.get(w_code, ("Clear", "☀️"))

            # Build 7-day forecast array
            daily_list = []
            dates = daily.get("time", [])
            max_temps = daily.get("temperature_2m_max", [])
            min_temps = daily.get("temperature_2m_min", [])
            d_codes = daily.get("weather_code", [])
            precips = daily.get("precipitation_sum", [])

            for i in range(min(7, len(dates))):
                c_desc, c_icon = WMO_CODE_MAP.get(d_codes[i] if i < len(d_codes) else 0, ("Clear", "☀️"))
                daily_list.append({
                    "date": dates[i],
                    "max_temp_c": round(max_temps[i], 1) if i < len(max_temps) else None,
                    "min_temp_c": round(min_temps[i], 1) if i < len(min_temps) else None,
                    "condition": c_desc,
                    "icon": c_icon,
                    "precipitation_mm": precips[i] if i < len(precips) else 0.0
                })

            result = {
                "is_live": True,
                "destination_name": dest_name,
                "source": "Open-Meteo API (Live)",
                "status_message": "Live meteorological conditions and 7-day forecast retrieved successfully.",
                "current": {
                    "temperature_c": round(curr.get("temperature_2m", 0.0), 1),
                    "feels_like_c": round(curr.get("apparent_temperature", 0.0), 1),
                    "humidity_percent": curr.get("relative_humidity_2m", 0),
                    "wind_speed_kmh": round(curr.get("wind_speed_10m", 0.0), 1),
                    "condition": condition_desc,
                    "icon": icon,
                    "timestamp": curr.get("time", "")
                },
                "climate_summary": climate_summary,
                "best_season": best_season,
                "daily_forecast": daily_list
            }

            # Cache the successful result
            _weather_cache[cache_key] = (now, result)
            return result
        else:
            return _build_fallback(dest_name, climate_summary, best_season, f"Weather API returned status code {resp.status_code}")

    except Exception as e:
        return _build_fallback(dest_name, climate_summary, best_season, f"Weather service offline ({type(e).__name__})")


def _build_fallback(dest_name: str, climate_summary: str, best_season: str, reason: str) -> Dict[str, Any]:
    """Graceful fallback response when live weather cannot be fetched."""
    return {
        "is_live": False,
        "destination_name": dest_name,
        "source": "Historical Climate Summary (Offline Fallback)",
        "status_message": f"{reason}. Displaying verified local climate profile.",
        "climate_summary": climate_summary,
        "best_season": best_season,
        "current": None,
        "daily_forecast": []
    }


def _build_error_fallback(msg: str) -> Dict[str, Any]:
    return {
        "is_live": False,
        "destination_name": "Unknown",
        "source": "None",
        "status_message": msg,
        "climate_summary": "",
        "best_season": "",
        "current": None,
        "daily_forecast": []
    }
