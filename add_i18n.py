import re

def update_html():
    with open('client/index.html', 'r', encoding='utf-8') as f:
        content = f.read()

    # Replacements
    replacements = {
        r'<title>.*?</title>': r'<title data-i18n="title">AI Soil Health Advisory System | Indian Farmer Portal</title>',
        r'<h2>AI Soil Health Advisory System</h2>': r'<h2 data-i18n="title">AI Soil Health Advisory System</h2>',
        r'<p>Empowering Indian farmers with precision agriculture and AI-driven insights.</p>': r'<p data-i18n="subtitle">Empowering Indian farmers with precision agriculture and AI-driven insights.</p>',
        r'<h3>Field Location</h3>': r'<h3 data-i18n="field_location">Field Location</h3>',
        r'<p class="map-hint">Click on your farm location to fetch weather data</p>': r'<p class="map-hint" data-i18n="map_hint">Click on your farm location to fetch weather data</p>',
        r'<h3>Soil Parameters</h3>': r'<h3 data-i18n="soil_params">Soil Parameters</h3>',
        r'<label for="nitrogen">Nitrogen \(N\)': r'<label for="nitrogen" data-i18n="nitrogen">Nitrogen (N)',
        r'<label for="phosphorus">Phosphorus \(P\)': r'<label for="phosphorus" data-i18n="phosphorus">Phosphorus (P)',
        r'<label for="potassium">Potassium \(K\)': r'<label for="potassium" data-i18n="potassium">Potassium (K)',
        r'<label for="ph">Soil pH</label>': r'<label for="ph" data-i18n="soil_ph">Soil pH</label>',
        r'<label for="moisture">Moisture \(%\)</label>': r'<label for="moisture" data-i18n="moisture">Moisture (%)</label>',
        r'<label for="soil_type">Soil Type</label>': r'<label for="soil_type" data-i18n="soil_type">Soil Type</label>',
        r'<label for="land_area">Land Area</label>': r'<label for="land_area" data-i18n="land_area">Land Area</label>',
        r'<label for="season">Season</label>': r'<label for="season" data-i18n="season">Season</label>',
        r'<label for="water_availability">Water Availability</label>': r'<label for="water_availability" data-i18n="water_avail">Water Availability</label>',
        r'<label for="preferred_crop">Preferred Crop \(Optional\)</label>': r'<label for="preferred_crop" data-i18n="preferred_crop">Preferred Crop (Optional)</label>',
        r'<p style="font-size: 0.75rem; color: var\(--text-muted\); margin-top: 5px;">We\'ll tell you how to prepare soil for this specific crop.</p>': r'<p style="font-size: 0.75rem; color: var(--text-muted); margin-top: 5px;" data-i18n="preferred_hint">We\'ll tell you how to prepare soil for this specific crop.</p>',
        r'<span>Generate Advisory</span>': r'<span data-i18n="generate_btn">Generate Advisory</span>',
        r'<p>AI is analyzing your soil data...</p>': r'<p data-i18n="loading_text">AI is analyzing your soil data...</p>',
        r'<h3>Your Preferred Crop Analysis</h3>': r'<h3 data-i18n="pref_analysis">Your Preferred Crop Analysis</h3>',
        r'<h3>Kharif Season \(Monsoon\)</h3>': r'<h3 data-i18n="kharif_season">Kharif Season (Monsoon)</h3>',
        r'<h3>Rabi Season \(Winter\)</h3>': r'<h3 data-i18n="rabi_season">Rabi Season (Winter)</h3>',
        r'<h3>Zaid & Perennial \(Summer/All-Year\)</h3>': r'<h3 data-i18n="zaid_season">Zaid & Perennial (Summer/All-Year)</h3>',
        r'<h3>Expert Regional Suggestions</h3>': r'<h3 data-i18n="expert_sugg">Expert Regional Suggestions</h3>',
        r'<h3>Fertilizer Requirements</h3>': r'<h3 data-i18n="fert_req">Fertilizer Requirements</h3>',
        r'<h3>Soil Corrections</h3>': r'<h3 data-i18n="soil_corr">Soil Corrections</h3>',
        r'<h3>AI Agricultural Advisory</h3>': r'<h3 data-i18n="ai_advisory">AI Agricultural Advisory</h3>',
        r'<h3>No Data Analyzed</h3>': r'<h3 data-i18n="no_data">No Data Analyzed</h3>',
        r'<p>Enter your soil parameters and click "Generate Advisory" to get personalized recommendations.</p>': r'<p data-i18n="no_data_desc">Enter your soil parameters and click "Generate Advisory" to get personalized recommendations.</p>',
        r'<p>&copy; 2024 AI Soil Management System for Indian Farmers. Built for sustainable agriculture.</p>': r'<p data-i18n="footer_text">&copy; 2024 AI Soil Management System for Indian Farmers. Built for sustainable agriculture.</p>',
        
        # Select options
        r'<option value="Sandy">Sandy</option>': r'<option value="Sandy" data-i18n="opt_sandy">Sandy</option>',
        r'<option value="Loamy">Loamy</option>': r'<option value="Loamy" data-i18n="opt_loamy">Loamy</option>',
        r'<option value="Clay">Clay</option>': r'<option value="Clay" data-i18n="opt_clay">Clay</option>',
        r'<option value="Black">Black</option>': r'<option value="Black" data-i18n="opt_black">Black</option>',
        r'<option value="Red">Red</option>': r'<option value="Red" data-i18n="opt_red">Red</option>',
        r'<option value="Acre">Acre</option>': r'<option value="Acre" data-i18n="opt_acre">Acre</option>',
        r'<option value="Hectare">Hectare</option>': r'<option value="Hectare" data-i18n="opt_hectare">Hectare</option>',
        r'<option value="Square Feet">Sq Ft</option>': r'<option value="Square Feet" data-i18n="opt_sqft">Sq Ft</option>',
        r'<option value="Kharif">Kharif</option>': r'<option value="Kharif" data-i18n="opt_kharif">Kharif</option>',
        r'<option value="Rabi">Rabi</option>': r'<option value="Rabi" data-i18n="opt_rabi">Rabi</option>',
        r'<option value="Zaid">Zaid</option>': r'<option value="Zaid" data-i18n="opt_zaid">Zaid</option>',
        r'<option value="Rainfed">Rainfed</option>': r'<option value="Rainfed" data-i18n="opt_rainfed">Rainfed</option>',
        r'<option value="Irrigated">Irrigated</option>': r'<option value="Irrigated" data-i18n="opt_irrigated">Irrigated</option>',
        r'<option value="Limited">Limited</option>': r'<option value="Limited" data-i18n="opt_limited">Limited</option>',
    }

    for pattern, rep in replacements.items():
        content = re.sub(pattern, rep, content)

    # Insert script tags
    if 'translations.js' not in content:
        content = content.replace('<script src="app.js"></script>', '<script src="translations.js"></script>\n    <script src="app.js"></script>')

    with open('client/index.html', 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == '__main__':
    update_html()
