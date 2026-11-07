"""
Weather Service — OpenWeatherMap API Integration
Fetches real-time weather for ANY location worldwide.
Fixed: better city name matching, state fallback, worldwide support.
"""

import httpx
from typing import Optional, Dict, Any
from app.config import settings


class WeatherService:

    BASE_URL = "https://api.openweathermap.org/data/2.5"
    GEO_URL  = "https://api.openweathermap.org/geo/1.0"

    async def get_current_weather(self, lat: float, lon: float) -> Optional[Dict[str, Any]]:
        """Fetch current weather by coordinates — works anywhere in the world."""
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(
                    f"{self.BASE_URL}/weather",
                    params={
                        "lat": lat,
                        "lon": lon,
                        "appid": settings.OPENWEATHER_API_KEY,
                        "units": "metric",
                    },
                )
                if response.status_code == 200:
                    return response.json()
                print(f"[ERROR] OpenWeatherMap coords error: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"[ERROR] Weather coords fetch error: {e}")
            return None

    async def get_coords_for_city(self, city: str, country: str = "IN") -> Optional[Dict]:
        """
        Use OpenWeatherMap Geocoding API to get lat/lon for any city name.
        This is more reliable than direct city name search.
        Works for any city worldwide.
        """
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                # Try with country code first
                response = await client.get(
                    f"{self.GEO_URL}/direct",
                    params={
                        "q": f"{city},{country}",
                        "limit": 1,
                        "appid": settings.OPENWEATHER_API_KEY,
                    },
                )
                if response.status_code == 200:
                    results = response.json()
                    if results:
                        return {"lat": results[0]["lat"], "lon": results[0]["lon"], "name": results[0]["name"]}

                # Retry without country code for worldwide search
                response2 = await client.get(
                    f"{self.GEO_URL}/direct",
                    params={
                        "q": city,
                        "limit": 1,
                        "appid": settings.OPENWEATHER_API_KEY,
                    },
                )
                if response2.status_code == 200:
                    results2 = response2.json()
                    if results2:
                        return {"lat": results2[0]["lat"], "lon": results2[0]["lon"], "name": results2[0]["name"]}

                print(f"[ERROR] Geocoding found no results for: {city}")
                return None
        except Exception as e:
            print(f"[ERROR] Geocoding error for {city}: {e}")
            return None

    async def get_weather_by_city(self, city: str, state: str = "", country: str = "IN") -> Optional[Dict[str, Any]]:
        """
        Fetch weather for any city worldwide.
        Uses geocoding for accurate results regardless of state/country.
        """
        try:
            # Build search query — try most specific first
            search_queries = []

            if state:
                search_queries.append(f"{city},{state},{country}")
            search_queries.append(f"{city},{country}")
            search_queries.append(city)  # worldwide fallback

            async with httpx.AsyncClient(timeout=15.0) as client:
                for query in search_queries:
                    response = await client.get(
                        f"{self.BASE_URL}/weather",
                        params={
                            "q": query,
                            "appid": settings.OPENWEATHER_API_KEY,
                            "units": "metric",
                        },
                    )
                    if response.status_code == 200:
                        print(f"[SUCCESS] Weather found for query: {query}")
                        return response.json()
                    print(f"[WARNING] Query '{query}' returned {response.status_code}, trying next...")

            # Last resort — use geocoding API to get coords then fetch by coords
            print(f"[PENDING] Trying geocoding fallback for: {city}")
            coords = await self.get_coords_for_city(city, country)
            if coords:
                return await self.get_current_weather(coords["lat"], coords["lon"])

            print(f"[ERROR] All attempts failed for city: {city}")
            return None

        except Exception as e:
            print(f"[ERROR] Weather city fetch error for {city}: {e}")
            return None

    async def get_weather_by_district_and_state(self, district: str, state: str) -> Optional[Dict[str, Any]]:
        """
        Specialized method for Indian districts.
        Tries multiple query formats to maximize success rate.
        """
        # Clean up common Indian district name issues
        clean_district = district.strip()
        clean_state = state.strip()

        # Try formats in order of reliability
        attempts = [
            (clean_district, clean_state, "IN"),
            (clean_district, "", "IN"),
            (clean_state, "", "IN"),   # Fall back to state capital if district fails
        ]

        for city, st, country in attempts:
            result = await self.get_weather_by_city(city, st, country)
            if result:
                return result

        return None

    def parse_weather(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse raw OpenWeatherMap response into clean format."""
        main    = data.get("main", {})
        weather = data.get("weather", [{}])[0]
        wind    = data.get("wind", {})
        rain    = data.get("rain", {})
        clouds  = data.get("clouds", {})

        return {
            "city":        data.get("name", ""),
            "temp":        round(main.get("temp", 0)),
            "feels_like":  round(main.get("feels_like", 0)),
            "humidity":    main.get("humidity", 0),
            "condition":   weather.get("main", ""),
            "description": weather.get("description", "").capitalize(),
            "icon":        weather.get("icon", ""),
            "wind_speed":  round(wind.get("speed", 0) * 3.6, 1),  # m/s → km/h
            "rain_1h":     rain.get("1h", 0),
            "cloudiness":  clouds.get("all", 0),
        }

    def should_send_alert(self, parsed: Dict[str, Any]) -> Optional[Dict[str, str]]:
        """
        Decide if weather warrants a push notification.
        Works for any location worldwide.
        """
        condition  = parsed.get("condition", "").lower()
        temp       = parsed.get("temp", 0)
        wind_speed = parsed.get("wind_speed", 0)
        rain_1h    = parsed.get("rain_1h", 0)
        humidity   = parsed.get("humidity", 0)
        city       = parsed.get("city", "your area")

        if "thunderstorm" in condition:
            return {
                "title": "⛈️ Thunderstorm Warning!",
                "body": f"Thunderstorm detected near {city}. Secure your crops and farm equipment immediately.",
                "alert_type": "thunderstorm",
            }
        if rain_1h >= 10 or "heavy rain" in condition:
            return {
                "title": "🌧️ Heavy Rain Alert!",
                "body": f"Heavy rainfall in {city}. Ensure proper drainage in your fields to prevent waterlogging.",
                "alert_type": "heavy_rain",
            }
        if "rain" in condition or rain_1h > 0:
            return {
                "title": "🌦️ Rain Expected",
                "body": f"Rain expected in {city} today. Good time to plan irrigation accordingly.",
                "alert_type": "rain",
            }
        if temp >= 42:
            return {
                "title": "🌡️ Extreme Heat Warning!",
                "body": f"Temperature is {temp}°C in {city}. Ensure proper irrigation. Avoid fieldwork during noon.",
                "alert_type": "extreme_heat",
            }
        if temp >= 38:
            return {
                "title": "☀️ High Temperature Alert",
                "body": f"It's {temp}°C in {city}. Increase irrigation frequency and protect crops from heat stress.",
                "alert_type": "heat",
            }
        if wind_speed >= 40:
            return {
                "title": "💨 Strong Wind Warning!",
                "body": f"Wind speed {wind_speed} km/h in {city}. Secure your crops, nets, and farm structures.",
                "alert_type": "strong_wind",
            }
        if humidity >= 90 and temp >= 25:
            return {
                "title": "🌫️ High Humidity Alert",
                "body": f"Humidity is {humidity}% in {city}. High risk of fungal disease. Check your crops carefully.",
                "alert_type": "humidity",
            }
        if temp <= 5:
            return {
                "title": "❄️ Cold Weather Alert",
                "body": f"Temperature dropping to {temp}°C in {city}. Protect sensitive crops from frost damage.",
                "alert_type": "cold",
            }

        return None


weather_service = WeatherService()
