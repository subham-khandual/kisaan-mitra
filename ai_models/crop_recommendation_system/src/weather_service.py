import os
import requests
import collections
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class WeatherService:
    def __init__(self):
        # Fallback support if dotenv path needs explicit loading
        env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
        if os.path.exists(env_path):
            load_dotenv(env_path)
            
        # Read API key securely from environment; use provided key as fallback
        self.api_key = os.getenv("WEATHER_API_KEY", "e4224448e3e0cadbf508170c39533e61").strip()
        self.geo_url = "http://api.openweathermap.org/geo/1.0/direct"
        self.weather_url = "https://api.openweathermap.org/data/2.5/weather"
        self.forecast_url = "https://api.openweathermap.org/data/2.5/forecast"

    def validate_location(self, district: str, state: str) -> dict:
        """
        Validate an Indian district and state using the OpenWeather Geocoding API.
        Guarantees only valid geographical spaces can be requested.
        """
        if not self.api_key:
            return {
                "status": "error",
                "message": "Weather API Key not configured. Please add WEATHER_API_KEY to your .env file."
            }
        
        if not district.strip() or not state.strip():
            return {
                "status": "error",
                "message": "Empty search query. Please select a valid state and district."
            }

        params = {
            "q": f"{district.strip()},{state.strip()},IN",
            "limit": 1,
            "appid": self.api_key
        }

        try:
            response = requests.get(self.geo_url, params=params, timeout=10)
            
            if response.status_code == 200:
                results = response.json()
                if results and len(results) > 0:
                    data = results[0]
                    # Ensure matching country matches India
                    if data.get("country", "IN") == "IN":
                        return {
                            "status": "success",
                            "lat": float(data.get("lat")),
                            "lon": float(data.get("lon")),
                            "name": data.get("name", district.strip()),
                            "state": data.get("state", state.strip()),
                            "country": "India"
                        }
                return {
                    "status": "invalid",
                    "message": "❌ Invalid Location. Could not verify district in the geocoding database."
                }
            elif response.status_code == 401:
                return {
                    "status": "error",
                    "message": "🔑 Invalid API Key. Please verify your OpenWeatherMap key in .env."
                }
            else:
                return {
                    "status": "error",
                    "message": f"OpenWeather geocoder error. Server responded with status: {response.status_code}"
                }
        except requests.exceptions.Timeout:
            return {
                "status": "error",
                "message": "⏱️ Connection Timeout. OpenWeather validation service is taking too long to respond."
            }
        except requests.exceptions.ConnectionError:
            return {
                "status": "error",
                "message": "🌐 Internet Failure. Please check your local network connection."
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Unexpected validation exception: {str(e)}"
            }

    def get_weather_by_coords(self, lat: float, lon: float, verified_name: str) -> dict:
        """
        Fetch real-time weather using coordinates.
        """
        params = {
            "lat": lat,
            "lon": lon,
            "appid": self.api_key,
            "units": "metric"
        }

        try:
            response = requests.get(self.weather_url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                main = data.get("main", {})
                wind = data.get("wind", {})
                weather_info = data.get("weather", [{}])[0]
                rain_info = data.get("rain", {})
                
                # Fetch rainfall in mm (1h or 3h fallback)
                rainfall = rain_info.get("1h", rain_info.get("3h", 0.0))
                
                return {
                    "status": "success",
                    "city": verified_name,
                    "temp": main.get("temp", 0.0),
                    "feels_like": main.get("feels_like", 0.0),
                    "humidity": main.get("humidity", 0),
                    "wind_speed": wind.get("speed", 0.0) * 3.6, # Convert m/s to km/h
                    "condition": weather_info.get("main", "Unknown"),
                    "description": weather_info.get("description", "No description").capitalize(),
                    "icon": weather_info.get("icon", "01d"),
                    "rainfall": float(rainfall),
                    "pressure": main.get("pressure", 1013),
                    "temp_min": main.get("temp_min", 0.0),
                    "temp_max": main.get("temp_max", 0.0),
                    "api_source": "OpenWeatherMap Live API (GPS verified)"
                }
            else:
                return {
                    "status": "error",
                    "message": f"Failed to fetch weather from verified coordinates. Status: {response.status_code}"
                }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Weather fetch exception: {str(e)}"
            }

    def get_5day_forecast_by_coords(self, lat: float, lon: float) -> dict:
        """
        Fetch 5-day / 3-hour forecast using coordinates.
        """
        params = {
            "lat": lat,
            "lon": lon,
            "appid": self.api_key,
            "units": "metric"
        }

        try:
            response = requests.get(self.forecast_url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                raw_list = data.get("list", [])
                
                # Group forecast records by day into structured daily metrics
                daily_forecasts = {}
                for item in raw_list:
                    dt_txt = item.get("dt_txt", "") # Format: "YYYY-MM-DD HH:MM:SS"
                    date_str = dt_txt.split(" ")[0] # Format: "YYYY-MM-DD"
                    
                    if date_str not in daily_forecasts:
                        daily_forecasts[date_str] = {
                            "temps": [],
                            "humidities": [],
                            "wind_speeds": [],
                            "rainfalls": [],
                            "conditions": [],
                            "descriptions": [],
                            "icons": []
                        }
                    
                    main = item.get("main", {})
                    wind = item.get("wind", {})
                    weather_info = item.get("weather", [{}])[0]
                    rain_info = item.get("rain", {})
                    
                    daily_forecasts[date_str]["temps"].append(main.get("temp", 0.0))
                    daily_forecasts[date_str]["humidities"].append(main.get("humidity", 0))
                    daily_forecasts[date_str]["wind_speeds"].append(wind.get("speed", 0.0))
                    daily_forecasts[date_str]["rainfalls"].append(rain_info.get("3h", 0.0))
                    daily_forecasts[date_str]["conditions"].append(weather_info.get("main", "Clear"))
                    daily_forecasts[date_str]["descriptions"].append(weather_info.get("description", ""))
                    daily_forecasts[date_str]["icons"].append(weather_info.get("icon", "01d"))

                # Compile structured daily averages
                summarized_forecast = []
                for date_str, metrics in list(daily_forecasts.items())[:5]: # Get exactly 5 days
                    avg_temp = sum(metrics["temps"]) / len(metrics["temps"])
                    avg_hum = sum(metrics["humidities"]) / len(metrics["humidities"])
                    avg_wind = (sum(metrics["wind_speeds"]) / len(metrics["wind_speeds"])) * 3.6
                    total_rain = sum(metrics["rainfalls"])
                    
                    # Find most frequent condition/icon code
                    cond_counter = collections.Counter(metrics["conditions"])
                    desc_counter = collections.Counter(metrics["descriptions"])
                    icon_counter = collections.Counter(metrics["icons"])
                    
                    summarized_forecast.append({
                        "date": date_str,
                        "temp_avg": round(avg_temp, 1),
                        "temp_min": round(min(metrics["temps"]), 1),
                        "temp_max": round(max(metrics["temps"]), 1),
                        "humidity_avg": round(avg_hum),
                        "wind_avg": round(avg_wind, 1),
                        "total_rain": round(total_rain, 1),
                        "condition": cond_counter.most_common(1)[0][0],
                        "description": desc_counter.most_common(1)[0][0].capitalize(),
                        "icon": icon_counter.most_common(1)[0][0]
                    })
                
                return {
                    "status": "success",
                    "forecast_list": summarized_forecast
                }
            else:
                return {
                    "status": "error",
                    "message": "Failed to pull weather forecast from verified coordinates."
                }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Forecast fetch exception: {str(e)}"
            }

    @staticmethod
    def get_agricultural_advice(weather_data: dict) -> dict:
        """
        Generate dynamic smart agricultural recommendations based on weather metrics.
        """
        temp = weather_data.get("temp", 25.0)
        humidity = weather_data.get("humidity", 60)
        rainfall = weather_data.get("rainfall", 0.0)
        wind = weather_data.get("wind_speed", 5.0)
        condition = weather_data.get("condition", "Clear").lower()
        
        alerts = []
        recommendations = []
        soil_insights = []
        suitable_crops = []
        
        # 1. Temperature-Based Alerts & Insights
        if temp >= 40.0:
            alerts.append("🔴 **EXTREME HEATWAVE ALERT**: Temperatures have breached 40°C. Protect crops from scorching.")
            soil_insights.append("🏜️ Extreme evaporation rates. Soil moisture depleting at critical speeds.")
            recommendations.append("💧 Schedule double irrigation early in the morning and late in the evening. Avoid mid-day irrigation as it causes water shock.")
            recommendations.append("🌾 Implement straw/leaf mulching to retain soil moisture and reduce surface temperature.")
            suitable_crops.extend(["Watermelon", "Muskmelon", "Sorghum", "Millet"])
        elif temp >= 35.0:
            alerts.append("🟠 **HIGH TEMPERATURE ALERT**: Elevated temperatures may cause vegetative stress.")
            soil_insights.append("📈 Rapid soil moisture loss. High transpiration stress detected.")
            recommendations.append("💧 Ensure frequent light watering. Keep high ventilation if using polyhouses.")
            suitable_crops.extend(["Cotton", "Pigeonpeas", "Maize", "Cowpea"])
        elif temp < 10.0:
            alerts.append("❄️ **COLD / FROST ALERT**: Low temperatures may slow down seedling growth.")
            soil_insights.append("📉 Low soil microbial activity due to cold. Nutrient uptake is naturally slower.")
            recommendations.append("🔥 Provide smoke cover or light evening sprinkler irrigation to elevate ambient temperatures and prevent frost damage.")
            suitable_crops.extend(["Wheat", "Barley", "Mustard", "Potato", "Chickpea"])
        else:
            soil_insights.append("🟢 Temperature is in the optimal range. Normal soil biological activity and nutrient uptake.")
            suitable_crops.extend(["Rice", "Maize", "Groundnut", "Banana", "Soybean"])
            
        # 2. Moisture & Rainfall-Based Insights
        if "thunderstorm" in condition or rainfall >= 15.0:
            alerts.append("⛈️ **STORMY / HEAVY RAINFALL ALERT**: Severe rainfall detected. Risk of waterlogging.")
            soil_insights.append("🌧️ Soil is saturated. High runoff risk. Leaching of soluble fertilizers may occur.")
            recommendations.append("🚫 **CRITICAL**: Postpone all chemical fertilizer or pesticide sprays immediately, as they will wash away.")
            recommendations.append("🚜 Clear all drainage channels to prevent water accumulation around root zones.")
            suitable_crops.extend(["Rice", "Jute", "Sugarcane"])
        elif "rain" in condition or rainfall > 0.0:
            alerts.append("🌧️ **RAIN DETECTED**: Natural precipitation active.")
            soil_insights.append("🌦️ Natural irrigation is active. Moisture levels are improving.")
            recommendations.append("💧 Suspend all artificial irrigation. Let natural rainfall absorb into root zones.")
            recommendations.append("🚫 Avoid spraying systemic herbicides or pesticides if rain is expected to continue.")
            suitable_crops.extend(["Rice", "Jute", "Coconut"])
        else:
            if humidity <= 40:
                soil_insights.append("🏜️ Dry air will increase soil evaporation rates. Top soil drying up.")
                recommendations.append("💧 Increase irrigation frequency. Light mulching is highly recommended.")
            elif humidity >= 85:
                alerts.append("🌫️ **HIGH HUMIDITY WARNING**: Humidity exceeds 85%. Favorable for fungal/pest growth.")
                soil_insights.append("🌾 Soil is damp, but high relative humidity blocks plant transpiration.")
                recommendations.append("🛡️ Monitor closely for powdery mildew, blight, or stem rot. Consider pre-emptive biological fungicide sprays.")

        # 3. Wind Speed Insights
        if wind >= 35.0:
            alerts.append("💨 **HIGH WINDS WARNING**: Wind speed exceeds 35 km/h. Risk of crop lodging (bending).")
            recommendations.append("🛡️ Provide structural support (staking) for tall crops like sugarcane, banana, and young saplings.")
            recommendations.append("🚫 Avoid tall canopy fertilizer dusting or high-pressure sprayers.")
            
        # Base recommendations if none generated
        if not recommendations:
            recommendations.append("🌾 Maintain standard weeding and soil aeration.")
            recommendations.append("🚜 Standard weeding and inspection for early pests is recommended.")
            
        return {
            "alerts": alerts,
            "soil_insights": soil_insights,
            "recommendations": recommendations,
            "suitable_crops": list(set(suitable_crops))
        }
