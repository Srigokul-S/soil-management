def calculate_fertilizer(land_area, unit, crop_name=None, season=None):
    """
    Base recommendation (per acre):
    - Urea -> 50 kg/acre
    - DAP -> 25 kg/acre
    - MOP -> 20 kg/acre
    """
    # Conversion factors to Acre
    conversions = {
        'Acre': 1.0,
        'Hectare': 2.47,
        'Square Feet': 1.0 / 43560
    }
    
    area_in_acres = land_area * conversions.get(unit, 1.0)
    
    # Base rates per acre
    urea_base = 50
    dap_base = 25
    mop_base = 20
    
    total_urea = urea_base * area_in_acres
    total_dap = dap_base * area_in_acres
    total_mop = mop_base * area_in_acres
    
    # Fertilizer schedule based on season
    if season == "Kharif":
        schedule = [
            {"stage": "Pre-sowing", "timing": "1 week before sowing", "action": f"Apply all DAP ({round(total_dap, 2)} kg) and MOP ({round(total_mop, 2)} kg) as basal dose"},
            {"stage": "First Top Dressing", "timing": "21-25 days after sowing", "action": f"Apply {round(total_urea * 0.33, 2)} kg Urea (1/3 of total)"},
            {"stage": "Second Top Dressing", "timing": "40-45 days after sowing", "action": f"Apply {round(total_urea * 0.33, 2)} kg Urea (1/3 of total)"},
            {"stage": "Third Top Dressing", "timing": "60-65 days after sowing", "action": f"Apply {round(total_urea * 0.34, 2)} kg Urea (remaining)"},
        ]
    elif season == "Rabi":
        schedule = [
            {"stage": "Pre-sowing", "timing": "At sowing time", "action": f"Apply all DAP ({round(total_dap, 2)} kg), MOP ({round(total_mop, 2)} kg), and 50% Urea ({round(total_urea * 0.5, 2)} kg)"},
            {"stage": "First Irrigation", "timing": "21 days after sowing", "action": f"Apply {round(total_urea * 0.25, 2)} kg Urea (25%)"},
            {"stage": "Second Irrigation", "timing": "45 days after sowing", "action": f"Apply {round(total_urea * 0.25, 2)} kg Urea (remaining 25%)"},
        ]
    else:
        schedule = [
            {"stage": "Basal Dose", "timing": "At planting", "action": f"Apply all DAP ({round(total_dap, 2)} kg) and MOP ({round(total_mop, 2)} kg)"},
            {"stage": "Top Dressing", "timing": "30 days after planting", "action": f"Apply {round(total_urea * 0.5, 2)} kg Urea (50%)"},
            {"stage": "Final Dose", "timing": "60 days after planting", "action": f"Apply {round(total_urea * 0.5, 2)} kg Urea (remaining 50%)"},
        ]
    
    return {
        "urea": f"{round(total_urea, 2)} kg",
        "dap": f"{round(total_dap, 2)} kg",
        "mop": f"{round(total_mop, 2)} kg",
        "breakdown": {
            "urea_per_acre": f"{urea_base} kg/acre",
            "dap_per_acre": f"{dap_base} kg/acre",
            "mop_per_acre": f"{mop_base} kg/acre",
            "calculated_acres": round(area_in_acres, 2)
        },
        "schedule": schedule
    }
