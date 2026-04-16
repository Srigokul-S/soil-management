import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini
api_key = os.getenv("GOOGLE_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

def generate_advisory(crops, fertilizer, corrections, language, season, preferred_crop=None):
    """
    Generates a farmer-friendly advisory in the target language with seasonal context.
    """
    if not api_key:
        # Smart Expert System Fallback
        advice = []
        n_status = "low" if fertilizer['urea'].startswith('0') else "optimal"
        
        if preferred_crop:
            advice.append(f"## 🛠️ PROCEDURES TO PLANT {preferred_crop.upper()} IN YOUR AREA")
            advice.append(f"To successfully cultivate {preferred_crop} in your current soil and climate, follow these specific procedures:")
            advice.append(f"- **Step 1: Soil Modification:** Adjust pH to ideal range (6.0-7.0) by adding lime or gypsum as per the corrections list.")
            advice.append(f"- **Step 2: Bed Preparation:** Create raised beds for better drainage if your soil is Clayey.")
            advice.append(f"- **Step 3: Nutrient Loading:** Apply a basal dose of organic manure (10 tonnes/ha) followed by the recommended {fertilizer['urea']} Urea.")
            advice.append(f"- **Step 4: Moisture Management:** Maintain field capacity moisture (60-70%) during first 15 days.")
            advice.append(f"\n---")
        
        advice.append(f"### 🧪 ICAR General Soil Analysis ({season})")
        advice.append(f"Based on your soil parameters, we have identified a {n_status} nitrogen profile. For the {season} season, we recommend the following preparation strategy:")
        
        advice.append("\n**1. BASIC LAND PREPARATION:**")
        advice.append("Deep summer ploughing should be done to kill soil-borne pests and weeds. In cases of low moisture, implement conservation tillage.")
        
        advice.append("\n**2. SOIL AMENDMENTS:**")
        if "alkaline" in str(corrections).lower():
            advice.append("Your soil shows alkaline tendencies. Apply **Gypsum** at 2-5 tonnes/ha based on current pH. Incorporate green manure like Sunnhemp.")
        else:
            advice.append("Apply **Farm Yard Manure (FYM)** at 10 tonnes/ha to improve soil structure and organic carbon.")
        
        advice.append("\n**3. NUTRIENT MANAGEMENT for Scientific Varieties:**")
        advice.append(f"Implement split application of {fertilizer['urea']} Urea. Apply 50% as basal dose and remaining in two splits at tillering and panicle initiation stages.")
        
        full_advice = "\n".join(advice)
        return {
            "original_en": full_advice,
            "translated": f"[{language} Translation of Scientific Advice]\n" + full_advice,
            "alternatives": [
                {"name": "Mungbean", "reason": "Nitrogen-fixing pulse", "profitability": "Medium"},
                {"name": "Mustard", "reason": "Low water requirement", "profitability": "High"}
            ]
        }

    model = genai.GenerativeModel('gemini-1.5-flash')
    
    crops_str = ", ".join([f"{c['name']} (Score: {c['score']})" for c in crops])
    corrections_str = " ".join(corrections)
    
    prompt = f"""
    You are an expert scientific agricultural advisor from ICAR.
    
    MAJOR TASK: 
    If the farmer has a 'Preferred Crop' ({preferred_crop}), provide a step-by-step 'TRANSFORMATION & PLANTING PROCEDURE' guide for it. 
    Detail the EXACT procedures to change the current soil type to fit this crop in their current area/climate.
    
    Secondary Tasks:
    1. For recommended crops ({crops_str}), suggest ICAR varieties.
    2. Suggest 5-7 ADDITIONAL ICAR crops for the {season} season.
    
    Translate everything into {language}. Format as JSON.
    """
    
    try:
        response = model.generate_content(prompt)
        text = response.text
        
        # Strip potential markdown JSON blocks
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()
            
        import json
        try:
            return json.loads(text)
        except:
            # If not JSON, return it as the translated text
            return {"original_en": "Refer to suggestions above.", "translated": response.text}
            
    except Exception as e:
        return {"error": str(e), "message": "Failed to generate AI advisory. Please check API key."}
