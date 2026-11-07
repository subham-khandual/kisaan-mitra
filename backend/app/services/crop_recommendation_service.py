"""
AI Crop Recommendation Service — Uses Groq API (Free, Fast).
Recommends next crops based on soil, weather, season, location, water availability.
"""

import httpx
import json
from typing import Dict, Any, List, Optional
from datetime import datetime


class CropRecommendationService:

    GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
    GROQ_MODEL = "llama-3.1-8b-instant"

    def get_current_season(self) -> str:
        """Auto-detect Indian farming season from current month."""
        month = datetime.now().month
        if month in [6, 7, 8, 9]:
            return "Kharif (Monsoon) — June to September"
        elif month in [10, 11, 12, 1, 2]:
            return "Rabi (Winter) — October to February"
        else:
            return "Zaid (Summer) — March to May"

    async def get_recommendations(
        self,
        soil_type: str,
        water_availability: str,
        previous_crop: str,
        weather: Dict[str, Any],
        land_size: Optional[str] = None,
        farming_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get AI crop recommendations using Groq API.
        Returns top 3 crops with detailed reasoning.
        """
        season = self.get_current_season()
        month  = datetime.now().strftime("%B")

        prompt = f"""You are an expert Indian agricultural scientist helping farmers choose the best crops.

FARMER'S DETAILS:
- Current Month: {month}
- Farming Season: {season}
- Soil Type: {soil_type}
- Water Availability: {water_availability}
- Previous Crop Grown: {previous_crop if previous_crop else 'None / First time'}
- Land Size: {land_size if land_size else 'Not specified'}
- Farming Type: {farming_type if farming_type else 'Conventional'}

REAL-TIME WEATHER CONDITIONS:
- Temperature: {weather.get('temp')}°C (Feels like {weather.get('feels_like')}°C)
- Humidity: {weather.get('humidity')}%
- Condition: {weather.get('condition')} — {weather.get('description')}
- Wind Speed: {weather.get('wind_speed')} km/h
- Rainfall (last 1hr): {weather.get('rain_1h')} mm

Based on ALL above parameters, recommend the TOP 3 most suitable crops for this farmer RIGHT NOW.

Consider:
1. Soil type compatibility
2. Current season and weather
3. Crop rotation (avoid same family as previous crop)
4. Water requirements vs availability
5. Market demand in the region
6. Expected profitability
7. Disease/pest risk in current weather

Respond ONLY in this exact JSON format, no other text or markdown:
{{
  "season": "{season}",
  "analysis_summary": "2-3 line summary of farming conditions",
  "recommendations": [
    {{
      "rank": 1,
      "crop": "Crop Name",
      "emoji": "single emoji for this crop",
      "confidence": 95,
      "why_suitable": "2-3 specific reasons this crop suits the conditions",
      "sowing_time": "Best sowing window e.g. First week of July",
      "harvest_time": "Expected harvest period",
      "expected_yield": "Expected yield per acre e.g. 20-25 quintals/acre",
      "water_need": "Low/Medium/High",
      "market_outlook": "Current market demand and price outlook",
      "key_care_tips": "2-3 important care tips for this crop in current conditions"
    }},
    {{
      "rank": 2,
      "crop": "Crop Name",
      "emoji": "single emoji",
      "confidence": 85,
      "why_suitable": "reasons",
      "sowing_time": "sowing window",
      "harvest_time": "harvest period",
      "expected_yield": "yield per acre",
      "water_need": "Low/Medium/High",
      "market_outlook": "price outlook",
      "key_care_tips": "care tips"
    }},
    {{
      "rank": 3,
      "crop": "Crop Name",
      "emoji": "single emoji",
      "confidence": 75,
      "why_suitable": "reasons",
      "sowing_time": "sowing window",
      "harvest_time": "harvest period",
      "expected_yield": "yield per acre",
      "water_need": "Low/Medium/High",
      "market_outlook": "price outlook",
      "key_care_tips": "care tips"
    }}
  ],
  "avoid_crops": ["crop1", "crop2"],
  "avoid_reason": "Why these crops should be avoided now"
}}"""

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.GROQ_URL,
                    headers={
                        "Authorization": f"Bearer {self._get_api_key()}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": self.GROQ_MODEL,
                        "messages": [
                            {
                                "role": "system",
                                "content": "You are an expert Indian agricultural scientist. Always respond with valid JSON only, no markdown, no extra text."
                            },
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        "temperature": 0.3,
                        "max_tokens": 1500,
                    },
                )

                if response.status_code != 200:
                    print(f"❌ Groq API error: {response.status_code} - {response.text}")
                    return self._fallback_recommendations(soil_type, season)

                data     = response.json()
                text     = data["choices"][0]["message"]["content"].strip()

                # Clean JSON if wrapped in backticks
                text = text.replace("```json", "").replace("```", "").strip()

                # Extract JSON if there's extra text
                start = text.find('{')
                end   = text.rfind('}') + 1
                if start != -1 and end > start:
                    text = text[start:end]

                parsed = json.loads(text)
                print(f"✅ Groq AI crop recommendations generated")
                return parsed

        except json.JSONDecodeError as e:
            print(f"❌ JSON parse error: {e}")
            return self._fallback_recommendations(soil_type, season)
        except Exception as e:
            print(f"❌ Groq API error: {e}")
            return self._fallback_recommendations(soil_type, season)

    def _get_api_key(self) -> str:
        from app.config import settings
        return settings.GROQ_API_KEY

    def _fallback_recommendations(self, soil_type: str, season: str) -> Dict[str, Any]:
        """Fallback if Groq API fails — rule-based recommendations."""
        month = datetime.now().month

        if month in [6, 7, 8, 9]:  # Kharif
            recs = [
                {"rank": 1, "crop": "Rice", "emoji": "🌾", "confidence": 90,
                 "why_suitable": "Perfect Kharif crop. Monsoon rains provide adequate water. High demand across India.",
                 "sowing_time": "June - July", "harvest_time": "October - November",
                 "expected_yield": "20-25 quintals/acre", "water_need": "High",
                 "market_outlook": "Stable demand. MSP support available.",
                 "key_care_tips": "Maintain 2-3 cm standing water. Watch for blast disease in humid weather."},
                {"rank": 2, "crop": "Maize", "emoji": "🌽", "confidence": 82,
                 "why_suitable": "Kharif maize grows well in warm temperatures. Lower water requirement than rice.",
                 "sowing_time": "June - July", "harvest_time": "September - October",
                 "expected_yield": "15-20 quintals/acre", "water_need": "Medium",
                 "market_outlook": "Growing demand for poultry feed. Good prices expected.",
                 "key_care_tips": "Apply nitrogen fertilizer in splits. Watch for stem borer."},
                {"rank": 3, "crop": "Soybean", "emoji": "🫘", "confidence": 75,
                 "why_suitable": "Excellent for soil health. Fixes nitrogen. Good market demand.",
                 "sowing_time": "June - July", "harvest_time": "October",
                 "expected_yield": "8-12 quintals/acre", "water_need": "Medium",
                 "market_outlook": "Strong demand from oil industry. Good export potential.",
                 "key_care_tips": "Avoid waterlogging. Inoculate seeds with Rhizobium."},
            ]
        elif month in [10, 11, 12, 1, 2]:  # Rabi
            recs = [
                {"rank": 1, "crop": "Wheat", "emoji": "🌾", "confidence": 92,
                 "why_suitable": "Best Rabi crop for North/Central India. Cool weather ideal for grain filling.",
                 "sowing_time": "October - November", "harvest_time": "March - April",
                 "expected_yield": "18-22 quintals/acre", "water_need": "Medium",
                 "market_outlook": "Strong MSP support. Consistent demand throughout year.",
                 "key_care_tips": "Irrigate at crown root initiation stage. Watch for yellow rust."},
                {"rank": 2, "crop": "Mustard", "emoji": "🌻", "confidence": 83,
                 "why_suitable": "Cool dry weather perfect for mustard. Low water requirement. High returns.",
                 "sowing_time": "October", "harvest_time": "February - March",
                 "expected_yield": "6-8 quintals/acre", "water_need": "Low",
                 "market_outlook": "Edible oil demand rising. Good export potential.",
                 "key_care_tips": "Apply sulfur fertilizer. Watch for aphids in February."},
                {"rank": 3, "crop": "Chickpea", "emoji": "🫘", "confidence": 76,
                 "why_suitable": "Rabi pulse. Fixes nitrogen in soil. Drought tolerant once established.",
                 "sowing_time": "October - November", "harvest_time": "February - March",
                 "expected_yield": "6-10 quintals/acre", "water_need": "Low",
                 "market_outlook": "Consistently high prices. Domestic demand strong.",
                 "key_care_tips": "Avoid excess irrigation. Watch for wilt disease."},
            ]
        else:  # Zaid
            recs = [
                {"rank": 1, "crop": "Watermelon", "emoji": "🍉", "confidence": 88,
                 "why_suitable": "High value summer crop. Excellent market demand. Grows well in heat.",
                 "sowing_time": "February - March", "harvest_time": "May - June",
                 "expected_yield": "80-100 quintals/acre", "water_need": "Medium",
                 "market_outlook": "Premium prices in summer. High demand in cities.",
                 "key_care_tips": "Use drip irrigation. Protect fruits from sunburn with straw mulch."},
                {"rank": 2, "crop": "Cucumber", "emoji": "🥒", "confidence": 80,
                 "why_suitable": "Fast growing summer vegetable. Quick returns in 45-50 days.",
                 "sowing_time": "February - March", "harvest_time": "April - May",
                 "expected_yield": "40-50 quintals/acre", "water_need": "Medium",
                 "market_outlook": "Good local market demand throughout summer.",
                 "key_care_tips": "Provide trellis support. Harvest regularly for continuous yield."},
                {"rank": 3, "crop": "Moong Dal", "emoji": "🫘", "confidence": 74,
                 "why_suitable": "Short duration crop 60-65 days. Improves soil fertility.",
                 "sowing_time": "March - April", "harvest_time": "May - June",
                 "expected_yield": "4-6 quintals/acre", "water_need": "Low",
                 "market_outlook": "Consistent demand. Price remains stable year round.",
                 "key_care_tips": "2-3 irrigations sufficient. Harvest when 80% pods mature."},
            ]

        return {
            "season": season,
            "analysis_summary": f"Based on current {season} season conditions. Recommendations use standard seasonal patterns.",
            "recommendations": recs,
            "avoid_crops": ["Same crop as previous season"],
            "avoid_reason": "Crop rotation is essential to maintain soil health and break pest/disease cycles.",
        }


crop_recommendation_service = CropRecommendationService()
