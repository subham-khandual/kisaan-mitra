"""
Dynamic Farming Tips Service — No paid API needed!
Generates personalized tips based on exact weather values + user's crops.
Pure logic — works 100% free.
"""

from typing import Dict, Any, List, Optional


class DynamicFarmingTipsService:

    # Crop-specific advice for different conditions
    CROP_HEAT_TIPS = {
        "maize":      "Irrigate Maize at base — avoid wetting leaves in heat.",
        "rice":       "Maintain 2-3 cm water level in paddy fields to cool roots.",
        "wheat":      "Wheat is heat-sensitive — irrigate immediately if temp > 35°C.",
        "tomato":     "Tomato flowers drop in extreme heat — provide shade if possible.",
        "onion":      "Onion bulbs may split in heat — ensure consistent moisture.",
        "cotton":     "Cotton tolerates heat but needs adequate water at boll stage.",
        "sugarcane":  "Sugarcane needs extra irrigation — increase by 20% in heat.",
        "soybean":    "Soybean pod filling is affected by heat — irrigate regularly.",
        "groundnut":  "Groundnut pegging is sensitive to heat — keep soil moist.",
        "sunflower":  "Sunflower heads may droop in extreme heat — irrigate daily.",
        "potato":     "Potato tuber formation stops above 30°C — mulch heavily.",
        "chilli":     "Chilli flowers drop above 38°C — provide afternoon shade.",
        "brinjal":    "Brinjal tolerates heat but needs consistent watering.",
        "cabbage":    "Cabbage bolts in heat — harvest early if heads are ready.",
        "cauliflower":"Cauliflower curds discolor in heat — cover with leaves.",
    }

    CROP_RAIN_TIPS = {
        "maize":      "Check Maize for stalk rot after heavy rain.",
        "rice":       "Rain is beneficial for paddy — check for blast disease.",
        "wheat":      "Avoid applying fertilizer before rain — it will wash away.",
        "tomato":     "Rain increases blight risk in tomatoes — inspect leaves.",
        "onion":      "Onion is highly susceptible to purple blotch after rain.",
        "cotton":     "Rain during cotton boll stage causes boll rot — monitor.",
        "sugarcane":  "Drain excess water from sugarcane fields quickly.",
        "soybean":    "Rain during flowering is fine — check for stem fly.",
        "groundnut":  "Waterlogging kills groundnut — ensure field drainage.",
        "potato":     "Rain increases late blight risk in potato — spray fungicide.",
        "chilli":     "Chilli roots rot in waterlogged soil — drain immediately.",
        "brinjal":    "Brinjal wilts easily in waterlogging — check drainage.",
    }

    CROP_HUMIDITY_TIPS = {
        "maize":      "High humidity increases Northern Leaf Blight in Maize.",
        "rice":       "Monitor paddy for Brown Spot and Sheath Blight in humidity.",
        "wheat":      "Wheat rust spreads fast in high humidity — inspect weekly.",
        "tomato":     "Early and Late Blight thrive in humidity — spray Mancozeb.",
        "onion":      "Thrips and downy mildew increase in high humidity.",
        "cotton":     "Whitefly and mealybug populations rise in humidity.",
        "potato":     "Late blight spreads rapidly — apply fungicide preventively.",
        "chilli":     "Anthracnose and powdery mildew risk is high — monitor.",
        "groundnut":  "Tikka disease (leaf spot) spreads fast in humidity.",
    }

    def generate_tips(
        self,
        weather: Dict[str, Any],
        crops: List[str],
        district: str,
        state: str,
    ) -> Dict[str, Any]:
        """
        Generate dynamic, personalized farming tips based on:
        - Exact weather values (temp, humidity, rain, wind)
        - User's specific crops
        - Location
        No paid API needed — pure logic.
        """
        temp       = weather.get("temp", 30)
        humidity   = weather.get("humidity", 60)
        wind_speed = weather.get("wind_speed", 0)
        rain_1h    = weather.get("rain_1h", 0)
        condition  = weather.get("condition", "").lower()
        description = weather.get("description", "")
        city       = weather.get("city", district)

        # Normalize crop names for matching
        crop_names_lower = [c.lower().strip() for c in crops]

        tips = []
        severity = "good"
        summary_parts = []

        # ── Thunderstorm ─────────────────────────────────────────────────
        if "thunderstorm" in condition:
            severity = "warning"
            summary_parts.append(f"Thunderstorm in {city}")
            tips.append("⚡ Do NOT go to the field — stay indoors until storm passes completely.")
            tips.append("🏠 Move all harvested produce, tools and equipment to covered storage.")
            tips.append("🚫 Switch off all electrical farm equipment and pumps immediately.")
            tips.append("📱 Keep monitoring weather — avoid field work for next 3-4 hours.")
            if any(c in crop_names_lower for c in ["maize", "sunflower", "sugarcane"]):
                tips.append("🌽 Tall crops like Maize/Sugarcane are prone to lodging — check after storm.")

        # ── Heavy Rain ───────────────────────────────────────────────────
        elif rain_1h >= 10 or "heavy rain" in condition:
            severity = "warning"
            summary_parts.append(f"Heavy rainfall {rain_1h}mm in {city}")
            tips.append("🌊 Check field drainage immediately — remove blockages to prevent waterlogging.")
            tips.append("🚫 Cancel all pesticide and fertilizer applications today.")
            tips.append("🏠 Protect harvested produce from moisture damage.")
            # Crop-specific rain tips
            for crop in crop_names_lower:
                if crop in self.CROP_RAIN_TIPS:
                    tips.append(f"🌾 {self.CROP_RAIN_TIPS[crop]}")
                    break

        # ── Light/Moderate Rain ──────────────────────────────────────────
        elif "rain" in condition or "drizzle" in condition or rain_1h > 0:
            severity = "caution"
            summary_parts.append(f"Rain expected in {city}")
            tips.append("💧 Skip irrigation today — rain will provide adequate moisture.")
            tips.append("🚫 Avoid spraying pesticides — rain will wash them away.")
            tips.append(f"🌡️ Current temperature {temp}°C with rain is ideal for crop growth.")
            for crop in crop_names_lower:
                if crop in self.CROP_RAIN_TIPS:
                    tips.append(f"🌾 {self.CROP_RAIN_TIPS[crop]}")
                    break

        # ── Extreme Heat ─────────────────────────────────────────────────
        elif temp >= 42:
            severity = "warning"
            summary_parts.append(f"Extreme heat {temp}°C in {city}")
            tips.append(f"🌡️ {temp}°C is dangerously hot — irrigate crops immediately and urgently.")
            tips.append("⏰ All field work must be done before 8 AM or after 6 PM only.")
            tips.append("🧑‍🌾 Protect yourself — wear a hat, carry water, avoid noon sun.")
            tips.append("🌿 Apply thick mulch layer around plants to retain soil moisture.")
            for crop in crop_names_lower:
                if crop in self.CROP_HEAT_TIPS:
                    tips.append(f"🌾 {self.CROP_HEAT_TIPS[crop]}")
                    break

        # ── High Heat ────────────────────────────────────────────────────
        elif temp >= 38:
            severity = "caution"
            summary_parts.append(f"High temperature {temp}°C in {city}")
            tips.append(f"☀️ {temp}°C — increase irrigation frequency by 30% today.")
            tips.append("⏰ Do field work early morning (before 9 AM) or after 5 PM.")
            tips.append("🌿 Check for wilting — irrigate immediately if leaves droop.")
            for crop in crop_names_lower:
                if crop in self.CROP_HEAT_TIPS:
                    tips.append(f"🌾 {self.CROP_HEAT_TIPS[crop]}")
                    break

        # ── High Humidity ────────────────────────────────────────────────
        elif humidity >= 88:
            severity = "caution"
            summary_parts.append(f"High humidity {humidity}% in {city}")
            tips.append(f"🌫️ {humidity}% humidity — high risk of fungal diseases today.")
            tips.append("🔍 Inspect all crops carefully for spots, mold or unusual colors.")
            tips.append("🌬️ Improve air circulation — avoid dense planting if possible.")
            tips.append("💊 Consider preventive fungicide spray in the evening.")
            for crop in crop_names_lower:
                if crop in self.CROP_HUMIDITY_TIPS:
                    tips.append(f"🌾 {self.CROP_HUMIDITY_TIPS[crop]}")
                    break

        # ── Strong Wind ──────────────────────────────────────────────────
        elif wind_speed >= 40:
            severity = "warning"
            summary_parts.append(f"Strong wind {wind_speed} km/h in {city}")
            tips.append(f"💨 Wind at {wind_speed} km/h — secure all farm structures now.")
            tips.append("🏗️ Tie shade nets, poly-houses and support poles immediately.")
            tips.append("🚿 Stop sprinkler irrigation — wind will waste all the water.")
            tips.append("🌱 Support tall crops with stakes to prevent lodging.")

        elif wind_speed >= 25:
            severity = "caution"
            summary_parts.append(f"Moderate wind {wind_speed} km/h in {city}")
            tips.append(f"💨 Wind at {wind_speed} km/h — avoid pesticide spraying today.")
            tips.append("🌱 Check if any young plants need additional support.")
            tips.append("🚿 Use drip irrigation instead of sprinklers in windy conditions.")

        # ── Cold Weather ─────────────────────────────────────────────────
        elif temp <= 5:
            severity = "warning"
            summary_parts.append(f"Very cold {temp}°C in {city}")
            tips.append(f"❄️ {temp}°C is very cold — protect sensitive crops from frost damage.")
            tips.append("🌱 Cover young seedlings and nursery plants with cloth overnight.")
            tips.append("💧 Reduce irrigation — plants absorb less water in cold weather.")
            tips.append("🔥 Light irrigation in the morning helps protect against frost.")

        elif temp <= 12:
            severity = "caution"
            summary_parts.append(f"Cool weather {temp}°C in {city}")
            tips.append(f"🌡️ {temp}°C — cool conditions slow crop growth slightly.")
            tips.append("💧 Reduce irrigation frequency — soil stays moist longer in cold.")
            tips.append("🌱 Good conditions for cool-season crops like wheat and mustard.")

        # ── Good Weather ─────────────────────────────────────────────────
        else:
            severity = "good"
            summary_parts.append(f"Good weather {temp}°C in {city}")
            tips.append(f"✅ {temp}°C with {humidity}% humidity — excellent conditions for farming.")
            tips.append("🌾 Great day for all field operations — sowing, weeding, spraying.")
            tips.append("💧 Maintain normal irrigation schedule today.")

            # Add crop-specific positive tips
            if crop_names_lower:
                crop_display = ", ".join(crops[:2])
                tips.append(f"🌱 Good time to inspect {crop_display} for any pest activity.")
                tips.append("🧪 Ideal conditions for fertilizer application if due.")

        # ── Add humidity warning even in good weather ────────────────────
        if severity == "good" and humidity >= 80:
            tips.append(f"⚠️ Humidity at {humidity}% — watch for early signs of fungal disease.")

        # ── Build summary ────────────────────────────────────────────────
        summary = f"{', '.join(summary_parts)} — {description}"
        if not summary.strip() or summary == " — ":
            summary = f"{temp}°C, {description} in {city}"

        # Limit to 4 tips max
        tips = tips[:4]

        return {
            "summary":  summary,
            "severity": severity,
            "tips":     tips,
        }


dynamic_farming_tips_service = DynamicFarmingTipsService()
