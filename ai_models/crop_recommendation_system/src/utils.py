import os
import requests
import numpy as np

# Ideal NPK and pH ranges for common crops in the dataset to calculate fertilizer and yield estimates
CROP_IDEALS = {
    'rice': {'N': 80, 'P': 40, 'K': 40, 'ph_min': 5.0, 'ph_max': 7.5, 'rainfall_min': 150, 'rainfall_max': 300, 'base_yield': 4.5},
    'maize': {'N': 80, 'P': 50, 'K': 20, 'ph_min': 5.5, 'ph_max': 7.0, 'rainfall_min': 60, 'rainfall_max': 120, 'base_yield': 5.5},
    'chickpea': {'N': 40, 'P': 60, 'K': 80, 'ph_min': 6.0, 'ph_max': 8.0, 'rainfall_min': 60, 'rainfall_max': 95, 'base_yield': 1.8},
    'kidneybeans': {'N': 20, 'P': 60, 'K': 20, 'ph_min': 5.5, 'ph_max': 6.0, 'rainfall_min': 60, 'rainfall_max': 150, 'base_yield': 2.0},
    'pigeonpeas': {'N': 20, 'P': 70, 'K': 20, 'ph_min': 4.5, 'ph_max': 7.5, 'rainfall_min': 90, 'rainfall_max': 200, 'base_yield': 1.5},
    'mothbeans': {'N': 25, 'P': 45, 'K': 20, 'ph_min': 3.5, 'ph_max': 9.0, 'rainfall_min': 30, 'rainfall_max': 75, 'base_yield': 0.8},
    'mungbean': {'N': 20, 'P': 50, 'K': 20, 'ph_min': 6.2, 'ph_max': 7.2, 'rainfall_min': 35, 'rainfall_max': 60, 'base_yield': 1.0},
    'blackgram': {'N': 40, 'P': 65, 'K': 20, 'ph_min': 6.5, 'ph_max': 7.8, 'rainfall_min': 60, 'rainfall_max': 75, 'base_yield': 1.2},
    'lentil': {'N': 20, 'P': 55, 'K': 20, 'ph_min': 5.8, 'ph_max': 9.0, 'rainfall_min': 35, 'rainfall_max': 100, 'base_yield': 1.4},
    'pomegranate': {'N': 40, 'P': 10, 'K': 40, 'ph_min': 5.5, 'ph_max': 7.0, 'rainfall_min': 50, 'rainfall_max': 100, 'base_yield': 12.0},
    'banana': {'N': 100, 'P': 80, 'K': 50, 'ph_min': 5.5, 'ph_max': 6.5, 'rainfall_min': 90, 'rainfall_max': 150, 'base_yield': 35.0},
    'mango': {'N': 30, 'P': 25, 'K': 30, 'ph_min': 5.5, 'ph_max': 7.0, 'rainfall_min': 50, 'rainfall_max': 100, 'base_yield': 8.0},
    'grapes': {'N': 30, 'P': 125, 'K': 125, 'ph_min': 5.0, 'ph_max': 7.0, 'rainfall_min': 40, 'rainfall_max': 70, 'base_yield': 15.0},
    'watermelon': {'N': 80, 'P': 25, 'K': 50, 'ph_min': 5.5, 'ph_max': 6.5, 'rainfall_min': 40, 'rainfall_max': 60, 'base_yield': 25.0},
    'muskmelon': {'N': 100, 'P': 25, 'K': 50, 'ph_min': 6.0, 'ph_max': 6.8, 'rainfall_min': 20, 'rainfall_max': 40, 'base_yield': 20.0},
    'apple': {'N': 120, 'P': 130, 'K': 200, 'ph_min': 5.5, 'ph_max': 6.5, 'rainfall_min': 100, 'rainfall_max': 250, 'base_yield': 22.0},
    'orange': {'N': 30, 'P': 10, 'K': 10, 'ph_min': 5.5, 'ph_max': 6.5, 'rainfall_min': 100, 'rainfall_max': 160, 'base_yield': 18.0},
    'papaya': {'N': 50, 'P': 50, 'K': 50, 'ph_min': 6.0, 'ph_max': 6.5, 'rainfall_min': 150, 'rainfall_max': 250, 'base_yield': 40.0},
    'coconut': {'N': 20, 'P': 15, 'K': 30, 'ph_min': 5.0, 'ph_max': 8.0, 'rainfall_min': 130, 'rainfall_max': 230, 'base_yield': 10.0},
    'cotton': {'N': 120, 'P': 40, 'K': 20, 'ph_min': 5.8, 'ph_max': 8.0, 'rainfall_min': 60, 'rainfall_max': 100, 'base_yield': 2.5},
    'jute': {'N': 80, 'P': 40, 'K': 40, 'ph_min': 6.0, 'ph_max': 7.5, 'rainfall_min': 150, 'rainfall_max': 205, 'base_yield': 2.2},
    'coffee': {'N': 100, 'P': 30, 'K': 30, 'ph_min': 6.0, 'ph_max': 6.5, 'rainfall_min': 120, 'rainfall_max': 180, 'base_yield': 1.5}
}

class AgTechUtils:
    @staticmethod
    def get_weather_data(city_name, api_key=None):
        """
        Fetch current weather from OpenWeatherMap API, or fallback to mock data.
        """
        if api_key and api_key.strip():
            try:
                url = f"https://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={api_key}&units=metric"
                res = requests.get(url, timeout=5)
                if res.status_code == 200:
                    data = res.json()
                    return {
                        'status': 'success',
                        'city': city_name,
                        'temp': data['main']['temp'],
                        'humidity': data['main']['humidity'],
                        'weather_desc': data['weather'][0]['description'].capitalize(),
                        'wind_speed': data['wind']['speed'],
                        'api_source': 'OpenWeatherMap API'
                    }
                else:
                    return {
                        'status': 'error',
                        'message': res.json().get('message', 'City not found')
                    }
            except Exception as e:
                print(f"[!] Weather API failed: {str(e)}")
                
        # Robust Falling back Mock Weather database based on city name matching
        city_lower = city_name.lower().strip()
        
        # Realistic climate regions fallback
        if 'mumbai' in city_lower or 'goa' in city_lower or 'kerala' in city_lower or 'chennai' in city_lower:
            temp, humidity, desc = 29.5, 84.0, "Warm & Humid Coastal climate"
        elif 'delhi' in city_lower or 'jaipur' in city_lower or 'rajasthan' in city_lower:
            temp, humidity, desc = 36.2, 38.0, "Hot & Dry Arid climate"
        elif 'shimla' in city_lower or 'kashmir' in city_lower or 'ooty' in city_lower or 'manali' in city_lower:
            temp, humidity, desc = 16.8, 62.0, "Cool & Clear Mountain climate"
        elif 'bangalore' in city_lower or 'pune' in city_lower or 'hyderabad' in city_lower:
            temp, humidity, desc = 26.5, 58.0, "Mild Pleasant Plateau climate"
        else:
            # Generic average Indian sub-continent climate
            temp, humidity, desc = 27.0, 65.0, "Scattered Clouds (Standard Climate)"
            
        return {
            'status': 'success',
            'city': city_name,
            'temp': temp,
            'humidity': humidity,
            'weather_desc': desc,
            'wind_speed': 3.4,
            'api_source': 'AgriMitra Climate Engine (Fallback Simulation)'
        }

    @staticmethod
    def recommend_fertilizers(n, p, k, target_crop):
        """
        Recommend fertilizers based on soil NPK levels and optimal crop requirements.
        """
        crop_key = target_crop.lower().strip()
        if crop_key not in CROP_IDEALS:
            return {
                'status': 'unknown_crop',
                'message': 'No baseline nutrition data available for this crop.'
            }
            
        ideals = CROP_IDEALS[crop_key]
        n_ideal, p_ideal, k_ideal = ideals['N'], ideals['P'], ideals['K']
        
        recommendations = []
        improvements = []
        
        # Calculate Deficits
        n_diff = n_ideal - n
        p_diff = p_ideal - p
        k_diff = k_ideal - k
        
        # Nitrogen Recommendation
        if n_diff > 15:
            recommendations.append({
                'element': 'Nitrogen (N)',
                'status': 'Deficient',
                'deficit': f"{n_diff:.1f} mg/kg",
                'fertilizer': 'Urea (46-0-0) or Ammonium Sulfate',
                'dose': f"Apply approx {n_diff * 2.2:.1f} kg/hectare of Urea",
                'role': 'Promotes lush leaf growth and vigorous stem development.'
            })
            improvements.append("Incorporate leguminous green manure crops (like alfalfa or clover) to naturally fix nitrogen.")
        elif n_diff < -30:
            improvements.append("High Nitrogen level! Avoid applying nitrogen fertilizers. Excess N causes hyper vegetative growth and weak stems.")
            
        # Phosphorus Recommendation
        if p_diff > 10:
            recommendations.append({
                'element': 'Phosphorus (P)',
                'status': 'Deficient',
                'deficit': f"{p_diff:.1f} mg/kg",
                'fertilizer': 'DAP (18-46-0) or Single Super Phosphate (SSP)',
                'dose': f"Apply approx {p_diff * 2.5:.1f} kg/hectare of DAP",
                'role': 'Essential for robust root growth, flowering, and seed development.'
            })
            improvements.append("Apply organic bone meal or rock phosphate to build long-term active phosphorus reserves.")
        elif p_diff < -20:
            improvements.append("High Phosphorus level! Excessive P can block the absorption of micronutrients like zinc and iron.")
            
        # Potassium Recommendation
        if k_diff > 10:
            recommendations.append({
                'element': 'Potassium (K)',
                'status': 'Deficient',
                'deficit': f"{k_diff:.1f} mg/kg",
                'fertilizer': 'MOP (Muriate of Potash - 0-0-60) or Potassium Sulfate',
                'dose': f"Apply approx {k_diff * 1.8:.1f} kg/hectare of MOP",
                'role': 'Boosts disease resistance, drought tolerance, and fruit/grain quality.'
            })
            improvements.append("Add hardwood ash or organic compost to increase potash availability.")
            
        if not recommendations:
            recommendations.append({
                'element': 'N, P, K Balanced',
                'status': 'Optimal',
                'deficit': 'None',
                'fertilizer': 'Organic Compost / Well-rotted manure',
                'dose': '5 tonnes/hectare as maintenance dose',
                'role': 'Maintains healthy soil organic carbon and balanced microbial life.'
            })
            
        return {
            'status': 'success',
            'crop': target_crop,
            'ideals': {'N': n_ideal, 'P': p_ideal, 'K': k_ideal},
            'deficits': {'N': n_diff, 'P': p_diff, 'K': k_diff},
            'recommendations': recommendations,
            'soil_actions': improvements
        }

    @staticmethod
    def analyze_soil_health(n, p, k, ph):
        """
        Evaluate soil health index (0 to 100) and provide pH-specific treatment suggestions.
        """
        score = 100
        remediation_tips = []
        pH_status = ""
        
        # pH evaluation
        if ph < 5.0:
            score -= 25
            pH_status = "Strongly Acidic (Critically Low)"
            remediation_tips.append("Apply agricultural lime (Calcium Carbonate) or Dolomite to raise soil pH to a neutral range.")
            remediation_tips.append("Ensure good soil aeration; acidic waterlogged soils limit nutrient absorption.")
        elif 5.0 <= ph < 6.0:
            score -= 10
            pH_status = "Slightly Acidic"
            remediation_tips.append("Incorporate wood ash or bone meal to naturally buffer acidity and raise pH.")
        elif 6.0 <= ph <= 7.2:
            pH_status = "Optimal Neutral (Excellent)"
            # No penalty
        elif 7.2 < ph <= 8.2:
            score -= 10
            pH_status = "Slightly Alkaline"
            remediation_tips.append("Apply organic matter, compost, or peat moss to naturally buffer alkalinity.")
        else:
            score -= 25
            pH_status = "Highly Alkaline (Critically High)"
            remediation_tips.append("Apply agricultural elemental sulfur or gypsum to reduce pH and neutralize alkaline salts.")
            remediation_tips.append("Use ammonium-based nitrogen fertilizers which have an acidifying effect.")
            
        # Nutrient balance evaluation
        low_nutrients = []
        for val, name in [(n, 'Nitrogen'), (p, 'Phosphorus'), (k, 'Potassium')]:
            if val < 25:
                score -= 10
                low_nutrients.append(name)
            elif val > 120:
                score -= 5 # Minor penalty for overload
                
        if low_nutrients:
            remediation_tips.append(f"Inadequate levels of: {', '.join(low_nutrients)}. Broad-spectrum organic compost application is highly recommended.")
        else:
            remediation_tips.append("NPK macronutrients show excellent base concentration; maintain with standard crop rotations.")
            
        # Bound score between 10 and 100
        score = max(10, min(100, score))
        
        if score >= 85:
            rating = "Excellent (Highly Fertile)"
            color = "#2ecc71"
        elif 70 <= score < 85:
            rating = "Good (Productive)"
            color = "#27ae60"
        elif 50 <= score < 70:
            rating = "Moderate (Needs Care)"
            color = "#f39c12"
        else:
            rating = "Poor (Critically Depleted)"
            color = "#e74c3c"
            
        return {
            'score': score,
            'rating': rating,
            'color': color,
            'ph_status': pH_status,
            'remediation': remediation_tips
        }

    @staticmethod
    def predict_crop_yield(n, p, k, temperature, humidity, ph, rainfall, recommended_crop):
        """
        Estimate crop yield in metric tonnes per hectare based on soil and weather deviations from ideal values.
        """
        crop_key = recommended_crop.lower().strip()
        if crop_key not in CROP_IDEALS:
            return {
                'expected_yield_t_ha': 3.5,
                'yield_level': 'Moderate (Estimated baseline)',
                'reasons': ['Baseline estimate due to sparse specific crop performance metrics.']
            }
            
        ideals = CROP_IDEALS[crop_key]
        base_yield = ideals['base_yield']
        
        # Scaling factor starts at 1.0 (100% of base yield)
        scaler = 1.0
        reasons = []
        
        # 1. pH evaluation
        if ph < ideals['ph_min']:
            dev = ideals['ph_min'] - ph
            reduction = min(0.3, dev * 0.15)
            scaler -= reduction
            reasons.append(f"Acidic soil (pH {ph:.2f}) restricts nutrient intake, lowering yield by {reduction*100:.1f}%.")
        elif ph > ideals['ph_max']:
            dev = ph - ideals['ph_max']
            reduction = min(0.3, dev * 0.15)
            scaler -= reduction
            reasons.append(f"Alkaline soil (pH {ph:.2f}) limits phosphorus and micronutrient uptake, lowering yield by {reduction*100:.1f}%.")
        else:
            scaler += 0.05
            reasons.append("Optimal soil pH enables highly efficient nutrient absorption (+5% yield boost).")
            
        # 2. Rainfall evaluation
        if rainfall < ideals['rainfall_min']:
            deficit = ideals['rainfall_min'] - rainfall
            reduction = min(0.4, (deficit / ideals['rainfall_min']) * 0.35)
            scaler -= reduction
            reasons.append(f"Rainfall deficit ({rainfall:.1f}mm vs min {ideals['rainfall_min']}mm required) causes water stress (-{reduction*100:.1f}% yield).")
        elif rainfall > ideals['rainfall_max']:
            excess = rainfall - ideals['rainfall_max']
            reduction = min(0.2, (excess / ideals['rainfall_max']) * 0.15)
            scaler -= reduction
            reasons.append(f"Excess rainfall ({rainfall:.1f}mm) may cause waterlogging and root rot (-{reduction*100:.1f}% yield).")
        else:
            scaler += 0.05
            reasons.append("Perfect rainfall levels support vigorous flowering and grain filling (+5% yield boost).")
            
        # 3. NPK nutrient evaluation
        # Calculate ratio of current NPK against ideal requirements
        n_ratio = min(1.2, n / ideals['N']) if ideals['N'] > 0 else 1.0
        p_ratio = min(1.2, p / ideals['P']) if ideals['P'] > 0 else 1.0
        k_ratio = min(1.2, k / ideals['K']) if ideals['K'] > 0 else 1.0
        
        avg_nutrient_ratio = (n_ratio + p_ratio + k_ratio) / 3.0
        
        if avg_nutrient_ratio < 0.6:
            scaler -= 0.2
            reasons.append("Severe nitrogen/potash deficiency severely limits growth capacity (-20% yield).")
        elif 0.6 <= avg_nutrient_ratio < 0.9:
            scaler -= 0.08
            reasons.append("Mild nutrient imbalances restrict full photosynthetic potential (-8% yield).")
        elif avg_nutrient_ratio > 1.05:
            scaler += 0.05
            reasons.append("Abundant macronutrient reserves support premium crop yield (+5% yield boost).")
            
        # Bind yield multiplier between 0.4 and 1.2
        scaler = max(0.4, min(1.2, scaler))
        final_yield = base_yield * scaler
        
        if scaler >= 1.0:
            level = "High (Optimal Conditions)"
        elif 0.75 <= scaler < 1.0:
            level = "Moderate (Average Conditions)"
        else:
            level = "Low (Sub-optimal Conditions)"
            
        return {
            'expected_yield_t_ha': round(final_yield, 2),
            'yield_level': level,
            'multiplier': round(scaler, 2),
            'reasons': reasons
        }

    @staticmethod
    def generate_download_text_report(n, p, k, temperature, humidity, ph, rainfall, prediction_results, soil_health, fertilizer_recs, yield_pred, city_weather=None):
        """
        Generate a professional text report of predictions and agricultural advice.
        """
        report = []
        report.append("="*65)
        report.append("          🌾 AGRI-MITRA AI CROP ADVISORY & SOIL ANALYSIS 🌾          ")
        report.append("="*65)
        report.append("\n[1] SOIL NUTRIENTS & ENVIRONMENTAL INPUTS:")
        report.append(f"    - Nitrogen (N):     {n} mg/kg")
        report.append(f"    - Phosphorus (P):   {p} mg/kg")
        report.append(f"    - Potassium (K):    {k} mg/kg")
        report.append(f"    - Soil pH:          {ph:.2f}")
        report.append(f"    - Temperature:      {temperature:.1f} °C")
        report.append(f"    - Humidity:         {humidity:.1f} %")
        report.append(f"    - Rainfall:         {rainfall:.1f} mm")
        
        if city_weather:
            report.append(f"\n[2] LOCAL WEATHER CONDITION ({city_weather.get('city', 'Selected City').upper()}):")
            report.append(f"    - Status:           {city_weather.get('weather_desc', 'N/A')}")
            report.append(f"    - Temperature:      {city_weather.get('temp', 'N/A')} °C")
            report.append(f"    - Humidity:         {city_weather.get('humidity', 'N/A')} %")
            report.append(f"    - API Engine:       {city_weather.get('api_source', 'N/A')}")
            
        report.append("\n[3] AI RECOMMENDATION RESULT:")
        report.append(f"    - Recommended Crop: {prediction_results['crop'].upper()}")
        report.append(f"    - Model Confidence: {prediction_results['confidence']*100:.2f} %")
        
        report.append("\n[4] SOIL HEALTH ANALYSIS:")
        report.append(f"    - Soil Health Score: {soil_health['score']}/100")
        report.append(f"    - Fertility Rating:  {soil_health['rating']}")
        report.append(f"    - pH Classification: {soil_health['ph_status']}")
        report.append("    - Actionable Remediation Tips:")
        for idx, tip in enumerate(soil_health['remediation'], 1):
            report.append(f"      {idx}. {tip}")
            
        report.append("\n[5] FERTILIZER PRESCRIPTION:")
        if fertilizer_recs['status'] == 'success':
            for rec in fertilizer_recs['recommendations']:
                report.append(f"    - {rec['element']} is {rec['status']}:")
                report.append(f"      * Deficit:      {rec['deficit']}")
                report.append(f"      * Prescription: {rec['fertilizer']}")
                report.append(f"      * Dose:         {rec['dose']}")
                report.append(f"      * Biological Role: {rec['role']}")
            report.append("    - Soil Organic Actions:")
            for idx, action in enumerate(fertilizer_recs['soil_actions'], 1):
                report.append(f"      {idx}. {action}")
        else:
            report.append(f"    - {fertilizer_recs.get('message', 'Nutrition reference data not available.')}")
            
        report.append("\n[6] CROP YIELD PREDICTION:")
        report.append(f"    - Estimated Yield:  {yield_pred['expected_yield_t_ha']} tonnes / hectare")
        report.append(f"    - Yield Rank:       {yield_pred['yield_level']}")
        report.append("    - Yield Factors:")
        for idx, reason in enumerate(yield_pred['reasons'], 1):
            report.append(f"      {idx}. {reason}")
            
        report.append("\n" + "="*65)
        report.append("    Disclaimer: Generated by AgriMitra AI. Apply with local farm trials.  ")
        report.append("="*65)
        
        return "\n".join(report)
