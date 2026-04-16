def get_soil_corrections(ph, soil_type, moisture):
    corrections = []
    
    if ph < 6.0:
        corrections.append("Soil is acidic. Add Lime (Calcium Carbonate) to increase pH.")
    elif ph > 8.0:
        corrections.append("Soil is alkaline. Add Gypsum (Calcium Sulfate) to lower pH.")
        
    if soil_type.lower() == 'sandy':
        corrections.append("Sandy soil has low water retention. Add organic compost or green manure.")
    elif soil_type.lower() == 'clay':
        corrections.append("Clay soil can cause waterlogging. Improve drainage systems and add gypsum to improve soil structure.")
        
    if moisture < 30:
        corrections.append("Low soil moisture detected. Implement scheduled irrigation or mulching to retain moisture.")
        
    if not corrections:
        corrections.append("Soil parameters are within optimal ranges for general cultivation.")
        
    return corrections
