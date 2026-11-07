# A heuristic mapping for the 22 crops in the dataset to give a slight probability boost 
# if a crop is highly suitable or historically grown in the given state.

STATE_CROP_AFFINITY = {
    "Andhra Pradesh": ["rice", "maize", "pigeonpeas", "cotton", "banana", "mango", "papaya", "coconut"],
    "Assam": ["rice", "jute", "banana", "papaya", "coconut"],
    "Bihar": ["rice", "maize", "chickpea", "mungbean", "lentil", "banana", "mango", "watermelon"],
    "Chhattisgarh": ["rice", "maize", "pigeonpeas"],
    "Goa": ["rice", "coconut", "banana", "mango", "coffee"],
    "Gujarat": ["cotton", "maize", "pigeonpeas", "banana", "papaya", "mango"],
    "Haryana": ["rice", "maize", "cotton", "chickpea", "lentil", "muskmelon"],
    "Himachal Pradesh": ["apple", "maize", "pomegranate", "kidneybeans"],
    "Jharkhand": ["rice", "maize", "pigeonpeas", "chickpea", "papaya"],
    "Karnataka": ["coffee", "maize", "rice", "cotton", "pomegranate", "banana", "mango", "coconut"],
    "Kerala": ["coconut", "coffee", "banana", "papaya", "rice", "mango"],
    "Madhya Pradesh": ["maize", "chickpea", "pigeonpeas", "mungbean", "blackgram", "cotton", "orange"],
    "Maharashtra": ["cotton", "pomegranate", "grapes", "banana", "orange", "mango", "pigeonpeas", "maize"],
    "Odisha": ["rice", "mungbean", "blackgram", "jute", "coconut", "banana"],
    "Punjab": ["rice", "maize", "cotton", "muskmelon", "chickpea", "lentil"],
    "Rajasthan": ["maize", "chickpea", "mothbeans", "mungbean", "cotton"],
    "Tamil Nadu": ["rice", "banana", "mango", "coconut", "cotton", "maize"],
    "Telangana": ["rice", "maize", "cotton", "mango", "papaya"],
    "Uttar Pradesh": ["rice", "maize", "chickpea", "lentil", "mango", "watermelon", "muskmelon", "banana"],
    "Uttarakhand": ["apple", "rice", "maize", "kidneybeans", "mango"],
    "West Bengal": ["rice", "jute", "banana", "coconut", "mango", "papaya"]
}

def adjust_probabilities_for_state(probabilities_dict: dict, state: str) -> dict:
    """
    Adjust the probabilities of the ML prediction based on state affinity.
    """
    if not state or state not in STATE_CROP_AFFINITY:
        return probabilities_dict
        
    affinity_crops = STATE_CROP_AFFINITY[state]
    adjusted = {}
    
    for crop, prob in probabilities_dict.items():
        if crop.lower() in affinity_crops:
            # Boost the probability by 25% (relative)
            adjusted[crop] = min(0.99, prob * 1.25)
        else:
            # Penalize heavily to enforce state suitability
            adjusted[crop] = max(0.01, prob * 0.4)
            
    # Re-normalize
    total = sum(adjusted.values())
    if total > 0:
        for crop in adjusted:
            adjusted[crop] = adjusted[crop] / total
            
    # Sort again descending
    return dict(sorted(adjusted.items(), key=lambda item: item[1], reverse=True))
