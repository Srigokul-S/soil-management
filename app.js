document.addEventListener('DOMContentLoaded', () => {
    const soilForm = document.getElementById('soilForm');
    const analyzeBtn = document.getElementById('analyzeBtn');
    const loading = document.getElementById('loading');
    const results = document.getElementById('results');
    const emptyState = document.getElementById('emptyState');
    const languageSelect = document.getElementById('language');

    // Translation logic
    function updateLanguage() {
        const lang = languageSelect.value;
        const dict = window.translations ? (window.translations[lang] || window.translations['English']) : null;
        
        if (!dict) return;

        const elementsToTranslate = document.querySelectorAll('[data-i18n]');
        elementsToTranslate.forEach(el => {
            const key = el.getAttribute('data-i18n');
            if (dict[key]) {
                // Preserve child spans if they exist (e.g., slider values)
                const childSpan = el.querySelector('span');
                if (childSpan) {
                    el.firstChild.nodeValue = dict[key] + ' ';
                } else if (el.tagName === 'OPTION') {
                    el.textContent = dict[key];
                } else {
                    el.textContent = dict[key];
                }
            }
        });
    }

    languageSelect.addEventListener('change', updateLanguage);
    updateLanguage();

    // API Base URL - use current origin if deployed, otherwise localhost
    const API_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' 
        ? 'http://localhost:8000' 
        : window.location.origin;

    // Weather State
    let weatherData = {
        temperature: 25.0,
        humidity: 60.0,
        rainfall: 100.0,
        location: "India"
    };

    // 0. Initialize Map
    const map = L.map('map').setView([20.5937, 78.9629], 5); // Center of India
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);

    let marker;

    map.on('click', async (e) => {
        const { lat, lng } = e.latlng;
        
        if (marker) map.removeLayer(marker);
        marker = L.marker([lat, lng]).addTo(map);
        
        await fetchWeather(lat, lng);
    });

    async function fetchWeather(lat, lon) {
        try {
            const res = await fetch(`https://api.open-meteo.com/v1/forecast?latitude=${lat}&longitude=${lon}&current=temperature_2m,relative_humidity_2m,precipitation&timezone=auto`);
            const data = await res.json();
            
            weatherData = {
                temperature: data.current.temperature_2m,
                humidity: data.current.relative_humidity_2m,
                rainfall: (data.current.precipitation || 0) * 10, // Approximate rainfall factor for model
                location: `Lat: ${lat.toFixed(2)}, Lon: ${lon.toFixed(2)}`
            };

            console.log("Weather updated:", weatherData);
            // Optional: alert user or update UI hint
            document.querySelector('.map-hint').innerHTML = `📍 Location Set! Temp: ${weatherData.temperature}°C | Hum: ${weatherData.humidity}%`;
            document.querySelector('.map-hint').style.color = 'var(--primary)';
        } catch (err) {
            console.error("Weather fetch failed:", err);
        }
    }

    // Slider Listeners
    const sliderMap = {
        'nitrogen': 'n-val',
        'phosphorus': 'p-val',
        'potassium': 'k-val'
    };

    Object.keys(sliderMap).forEach(type => {
        const slider = document.getElementById(type);
        const display = document.getElementById(sliderMap[type]);
        slider.addEventListener('input', () => {
            display.textContent = `${slider.value}%`;
        });
    });

    soilForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        // 1. Collect Form Data
        const formData = {
            nitrogen: parseFloat(document.getElementById('nitrogen').value) * 1.4,
            phosphorus: parseFloat(document.getElementById('phosphorus').value) * 1.45,
            potassium: parseFloat(document.getElementById('potassium').value) * 2.05,
            ph: parseFloat(document.getElementById('ph').value),
            moisture: parseFloat(document.getElementById('moisture').value),
            soil_type: document.getElementById('soil_type').value,
            land_area: parseFloat(document.getElementById('land_area').value),
            land_unit: document.getElementById('land_unit').value,
            season: document.getElementById('season').value,
            water_availability: document.getElementById('water_availability').value,
            preferred_crop: document.getElementById('preferred_crop').value,
            language: languageSelect.value,
            ...weatherData
        };

        // 2. Show Loading State
        toggleUI('loading');

        try {
            // 3. API Call
            const response = await fetch(`${API_URL}/predict`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to analyze soil data.');
            }

            const data = await response.json();

            // 4. Update UI with Results
            updateResults(data);
            toggleUI('results');

        } catch (error) {
            console.error('Error:', error);
            alert(`Error: ${error.message}`);
            toggleUI('empty');
        }
    });

    function toggleUI(state) {
        loading.classList.add('hidden');
        results.classList.add('hidden');
        emptyState.classList.add('hidden');

        if (state === 'loading') {
            loading.classList.remove('hidden');
        } else if (state === 'results') {
            results.classList.remove('hidden');
        } else {
            emptyState.classList.remove('hidden');
        }
    }

    function updateResults(data) {
        // A. Categorized Crops
        const kharifList = document.getElementById('kharifList');
        const rabiList = document.getElementById('rabiList');
        const zaidList = document.getElementById('zaidList');

        if (kharifList) kharifList.innerHTML = '';
        if (rabiList) rabiList.innerHTML = '';
        if (zaidList) zaidList.innerHTML = '';

        if (data.crops) {
            data.crops.forEach(crop => {
                const card = document.createElement('div');
                card.className = 'crop-card';
                    card.innerHTML = `
                        <div class="crop-icon-box">
                            <i data-lucide="leaf"></i>
                        </div>
                        <h4>${crop.name}</h4>
                        <p class="crop-category">${crop.category}</p>
                        <div class="badge-row">
                            <div class="score-badge ${crop.color}">${crop.score}% Match</div>
                            ${crop.is_seasonal ? '<div class="season-badge">Seasonal</div>' : '<div class="season-badge warning">Off-Season</div>'}
                        </div>
                        <span class="cost-tag">Investment: ${crop.cost}</span>
                    `;

                // Add to correct seasonal bucket
                if (crop.season_type === 'Kharif' && kharifList) {
                    kharifList.appendChild(card);
                } else if (crop.season_type === 'Rabi' && rabiList) {
                    rabiList.appendChild(card);
                } else if (zaidList) {
                    zaidList.appendChild(card);
                }
            });
        }

        // B. Fertilizer
        const fertInfo = document.getElementById('fertilizerInfo');
        if (fertInfo && data.fertilizer) {
            fertInfo.innerHTML = `
                <div class="fertilizer-item">
                    <span>Urea Requirement</span>
                    <span class="fertilizer-val">${data.fertilizer.urea}</span>
                </div>
                <div class="fertilizer-item">
                    <span>DAP Requirement</span>
                    <span class="fertilizer-val">${data.fertilizer.dap}</span>
                </div>
                <div class="fertilizer-item">
                    <span>MOP Requirement</span>
                    <span class="fertilizer-val">${data.fertilizer.mop}</span>
                </div>
                <p style="margin-top: 15px; font-size: 0.85rem; color: #666;">
                    <strong>Schedule:</strong> ${data.fertilizer.schedule}
                </p>
            `;
        }

        // C. Corrections
        const correctionList = document.getElementById('correctionList');
        if (correctionList && data.soil_correction) {
            correctionList.innerHTML = '';
            data.soil_correction.forEach(text => {
                const li = document.createElement('li');
                li.className = 'correction-item';
                li.innerHTML = `<i data-lucide="check-circle-2"></i> <span>${text}</span>`;
                correctionList.appendChild(li);
            });
        }

        // D. Regional Alternatives
        const alternativesList = document.getElementById('alternativesList');
        if (alternativesList) {
            alternativesList.innerHTML = '';
            if (data.advisory && data.advisory.alternatives) {
                data.advisory.alternatives.forEach(alt => {
                    const card = document.createElement('div');
                    card.className = 'alt-card';
                    card.innerHTML = `
                        <div class="alt-info">
                            <strong>${alt.name}</strong>
                            <p>${alt.reason}</p>
                        </div>
                        <span class="profit-tag ${alt.profitability ? alt.profitability.toLowerCase() : 'medium'}">Profit: ${alt.profitability || 'Medium'}</span>
                    `;
                    alternativesList.appendChild(card);
                });
            }
        }

        // E. Advisory
        const advisoryText = document.getElementById('advisoryText');
        if (advisoryText) {
            let displayAdvisory = "";
            if (data.advisory && typeof data.advisory === 'object') {
                displayAdvisory = data.advisory.translated || data.advisory.original_en || "Advisory generated.";
            } else {
                displayAdvisory = data.advisory || "No advisory available.";
            }
            advisoryText.innerHTML = displayAdvisory;
        }

        // F. Preferred Crop Analysis
        const preferredSection = document.getElementById('preferredSection');
        if (preferredSection) {
            const analysis = data.advisory ? data.advisory.preferred_analysis : null;
            if (analysis && analysis.status) {
                preferredSection.classList.remove('hidden');
                document.getElementById('preferredCropName').textContent = document.getElementById('preferred_crop').value;
                document.getElementById('preferredReason').textContent = analysis.reason;
                
                const statusDiv = document.getElementById('preferredStatus');
                statusDiv.textContent = analysis.status;
                statusDiv.className = `status-indicator ${analysis.status === 'POSSIBLE' ? 'status-possible' : 'status-avoid'}`;
                
                const stepsDiv = document.getElementById('preferredSteps');
                stepsDiv.innerHTML = '';
                analysis.steps.forEach(step => {
                    const item = document.createElement('div');
                    item.className = 'step-item';
                    item.textContent = step;
                    stepsDiv.appendChild(item);
                });
            } else {
                preferredSection.classList.add('hidden');
            }
        }

        // Refresh Lucide Icons
        if (window.lucide) {
            lucide.createIcons();
        }
    }
});
