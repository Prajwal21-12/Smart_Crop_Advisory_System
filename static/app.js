// ============================================================
// SMART CROP ADVISORY SYSTEM
// FRONTEND JAVASCRIPT - COMPLETE FIXED VERSION
// ============================================================


// ------------------------------------------------------------
// HELPER
// ------------------------------------------------------------

function $(id) {
    return document.getElementById(id);
}


// ------------------------------------------------------------
// GLOBAL RESULTS
// ------------------------------------------------------------

let latestDiseaseResult = null;
let latestFarmResult = null;


// ------------------------------------------------------------
// TRANSLATIONS
// ------------------------------------------------------------

const translations = {

    en: {
        farmerProfileTitle: "1. Farmer & Farm Profile",
        soilConditionsTitle: "2. Soil & Field Conditions",
        cropRecommendationTitle: "3. AI Crop Recommendation",
        diseaseAITitle: "4. Plant Disease AI",
        actionPlanTitle: "5. Smart Farm Action Plan",

        saveProfile: "💾 Save farmer profile",
        recommendation: "🌱 Get Smart Recommendation",
        analyzeLeaf: "🔍 Analyze Leaf Image",

        cropDecision: "🌱 Crop Decision",
        plantHealth: "🌿 Plant Health",
        weatherAction: "🌦️ Weather-Based Action",
        irrigationAction: "💧 Irrigation Action",
        nutrientAction: "🧪 Nutrient Action",
        riskAlerts: "⚠️ Risk Alerts",
        nextSteps: "📋 Farmer's Next Steps"
    },

    kn: {
        farmerProfileTitle: "1. ರೈತ ಮತ್ತು ಜಮೀನು ವಿವರಗಳು",
        soilConditionsTitle: "2. ಮಣ್ಣು ಮತ್ತು ಜಮೀನಿನ ಪರಿಸ್ಥಿತಿಗಳು",
        cropRecommendationTitle: "3. AI ಬೆಳೆ ಶಿಫಾರಸು",
        diseaseAITitle: "4. ಸಸ್ಯ ರೋಗ AI",
        actionPlanTitle: "5. ಸ್ಮಾರ್ಟ್ ಕೃಷಿ ಕಾರ್ಯ ಯೋಜನೆ",

        saveProfile: "💾 ರೈತರ ವಿವರ ಉಳಿಸಿ",
        recommendation: "🌱 ಸ್ಮಾರ್ಟ್ ಶಿಫಾರಸು ಪಡೆಯಿರಿ",
        analyzeLeaf: "🔍 ಎಲೆ ಚಿತ್ರ ವಿಶ್ಲೇಷಿಸಿ",

        cropDecision: "🌱 ಬೆಳೆ ನಿರ್ಧಾರ",
        plantHealth: "🌿 ಸಸ್ಯ ಆರೋಗ್ಯ",
        weatherAction: "🌦️ ಹವಾಮಾನ ಆಧಾರಿತ ಕ್ರಮ",
        irrigationAction: "💧 ನೀರಾವರಿ ಕ್ರಮ",
        nutrientAction: "🧪 ಪೋಷಕಾಂಶ ಕ್ರಮ",
        riskAlerts: "⚠️ ಅಪಾಯ ಎಚ್ಚರಿಕೆಗಳು",
        nextSteps: "📋 ರೈತರ ಮುಂದಿನ ಕ್ರಮಗಳು"
    },

    hi: {
        farmerProfileTitle: "1. किसान और खेत प्रोफ़ाइल",
        soilConditionsTitle: "2. मिट्टी और खेत की स्थिति",
        cropRecommendationTitle: "3. AI फसल सिफारिश",
        diseaseAITitle: "4. पौधों की बीमारी AI",
        actionPlanTitle: "5. स्मार्ट फार्म एक्शन प्लान",

        saveProfile: "💾 किसान प्रोफ़ाइल सेव करें",
        recommendation: "🌱 स्मार्ट सिफारिश प्राप्त करें",
        analyzeLeaf: "🔍 पत्ती की तस्वीर का विश्लेषण करें",

        cropDecision: "🌱 फसल निर्णय",
        plantHealth: "🌿 पौधे का स्वास्थ्य",
        weatherAction: "🌦️ मौसम आधारित कार्रवाई",
        irrigationAction: "💧 सिंचाई कार्रवाई",
        nutrientAction: "🧪 पोषक तत्व कार्रवाई",
        riskAlerts: "⚠️ जोखिम चेतावनी",
        nextSteps: "📋 किसान के अगले कदम"
    }
};


// ------------------------------------------------------------
// LANGUAGE
// ------------------------------------------------------------

function changeLanguage() {
    const languageElement = document.getElementById("language");

    if (!languageElement) {
        console.error("Language dropdown not found!");
        return;
    }

    const selected = languageElement.value;

    // Support both English/Kannada/Hindi and en/kn/hi values
    const languageMap = {
        "English": "en",
        "Kannada": "kn",
        "Hindi": "hi",
        "en": "en",
        "kn": "kn",
        "hi": "hi"
    };

    const lang = languageMap[selected] || "en";
    const t = translations[lang];

    if (!t) {
        console.error("Translation not found:", lang);
        return;
    }

    console.log("Language changed to:", lang);

    // Main headings
    const elements = {
        farmerProfileTitle: t.farmerProfileTitle,
        soilConditionsTitle: t.soilConditionsTitle,
        cropRecommendationTitle: t.cropRecommendationTitle,
        diseaseAITitle: t.diseaseAITitle,
        actionPlanTitle: t.actionPlanTitle
    };

    Object.keys(elements).forEach(function (id) {
        const element = document.getElementById(id);

        if (element && elements[id]) {
            element.textContent = elements[id];
        }
    });

    // Recommendation button
    const recommendBtn = document.getElementById("recommendBtn");

    if (recommendBtn && t.getRecommendation) {
        recommendBtn.textContent = t.getRecommendation;
    }

    // Disease button
    const diseaseButton = document.querySelector(
        'button[onclick="uploadLeaf()"]'
    );

    if (diseaseButton && t.analyzeLeaf) {
        diseaseButton.textContent = t.analyzeLeaf;
    }

    // Print button
    const printButton = document.getElementById("printReportBtn");

    if (printButton && t.printReport) {
        printButton.textContent = t.printReport;
    }

    // Action plan
    if (typeof generateActionPlan === "function" && latestFarmResult) {
        generateActionPlan();
    }
}

// ------------------------------------------------------------
// SAVE FARMER PROFILE
// ------------------------------------------------------------

async function saveProfile() {

    try {

        const name = $("name")?.value?.trim() || "";
        const location = $("location")?.value?.trim() || "";
        const landArea = parseFloat($("landArea")?.value) || 0;
        const soilType = $("soilType")?.value || "";
        const water = $("water")?.value || "";
        const language = $("language")?.value || "en";

        if (!name) {
            alert("Please enter farmer name.");
            return;
        }

        if (!location) {
            alert("Please select a location.");
            return;
        }

        const response = await fetch("/api/save-farmer", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({

                name: name,
                location: location,
                land_area: landArea,
                soil_type: soilType,

                // Send both names for backend compatibility
                water: water,
                water_availability: water,

                language: language
            })
        });


        const text = await response.text();

        let data;

        try {
            data = JSON.parse(text);
        } catch (error) {
            throw new Error(
                "Server returned invalid response: " +
                text.substring(0, 200)
            );
        }


        if (!response.ok) {

            throw new Error(
                data.error ||
                data.message ||
                "Unable to save farmer profile."
            );
        }


        alert(
            data.message ||
            "Farmer profile saved successfully."
        );


    } catch (error) {

        console.error("Save profile error:", error);

        alert(
            "Unable to save farmer profile.\n\n" +
            error.message
        );
    }
}


// ------------------------------------------------------------
// GET SMART RECOMMENDATION
// ------------------------------------------------------------

async function recommend() {

    try {

        // ----------------------------------------------------
        // READ FORM VALUES
        // ----------------------------------------------------
        const farmerName =
            $("farmerName")?.value?.trim() || "";
        const location =
            $("location")?.value?.trim() || "";

        const nitrogen =
            parseFloat($("nitrogen")?.value);

        const phosphorus =
            parseFloat($("phosphorus")?.value);

        const potassium =
            parseFloat($("potassium")?.value);

        const ph =
            parseFloat($("soilPH")?.value);

        const moisture =
            parseFloat($("moisture")?.value);

        const rainfall =
            parseFloat($("rainfall")?.value);

        const temperature =
            parseFloat($("temperature")?.value);

        const soilType =
            $("soilType")?.value || "";

        const water =
            $("water")?.value || "";

        const landArea =
            parseFloat($("landArea")?.value) || 0;


        // ----------------------------------------------------
        // VALIDATION
        // ----------------------------------------------------

        if (!location) {
            alert("Please select a location.");
            return;
        }

        if (Number.isNaN(nitrogen)) {
            alert("Please enter Nitrogen value.");
            return;
        }

        if (Number.isNaN(phosphorus)) {
            alert("Please enter Phosphorus value.");
            return;
        }

        if (Number.isNaN(potassium)) {
            alert("Please enter Potassium value.");
            return;
        }

        if (Number.isNaN(ph)) {
            alert("Please enter Soil pH.");
            return;
        }

        if (Number.isNaN(moisture)) {
            alert("Please enter Soil moisture.");
            return;
        }

        if (Number.isNaN(rainfall)) {
            alert("Please enter expected rainfall.");
            return;
        }

        if (Number.isNaN(temperature)) {
            alert("Please enter temperature.");
            return;
        }


        // ----------------------------------------------------
        // SHOW LOADING
        // ----------------------------------------------------

        const button =
            document.querySelector(
                'button[onclick="recommend()"]'
            );

        const oldButtonText =
            button ? button.textContent : "";

        if (button) {
            button.disabled = true;
            button.textContent = "⏳ Generating recommendation...";
        }


        // ----------------------------------------------------
        // SEND DATA TO FLASK
        // ----------------------------------------------------

        const response = await fetch("/api/recommend", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({

                // Main names
                n: nitrogen,
                p: phosphorus,
                k: potassium,

                ph: ph,
                moisture: moisture,
                rainfall: rainfall,
                temp: temperature,

                name: document.getElementById("name")?.value.trim() || farmerName,
                farmer_name: document.getElementById("name")?.value.trim() || farmerName,
                location: location,

                soil_type: soilType,
                water: water,
                water_availability: water,
                land_area: landArea
            })
        });


        // ----------------------------------------------------
        // READ RESPONSE SAFELY
        // ----------------------------------------------------

        const responseText =
            await response.text();

        let d;

        try {

            d = JSON.parse(responseText);

        } catch (error) {

            console.error(
                "Invalid server response:",
                responseText
            );

            throw new Error(
                "Server returned an invalid response."
            );
        }


        if (!response.ok) {

            console.error(
                "Recommendation server error:",
                d
            );

            throw new Error(
                d.error ||
                d.message ||
                "Unable to generate recommendation."
            );
        }


        // ----------------------------------------------------
        // SAVE RESULT
        // ----------------------------------------------------

        latestFarmResult = d;


        // ----------------------------------------------------
        // SHOW RESULTS
        // ----------------------------------------------------

        const results =
            $("results");

        if (results) {
            results.classList.remove("hidden");
        }


        // ----------------------------------------------------
        // CROP RECOMMENDATIONS
        // ----------------------------------------------------

        renderCropRecommendations(d);


        // ----------------------------------------------------
        // WEATHER
        // ----------------------------------------------------

        renderWeather(d);


        // ----------------------------------------------------
        // IRRIGATION
        // ----------------------------------------------------

        renderIrrigation(d);


        // ----------------------------------------------------
        // NUTRIENTS
        // ----------------------------------------------------

        renderNutrients(d);


        // ----------------------------------------------------
        // ALERTS
        // ----------------------------------------------------

        renderAlerts(d);


        // ----------------------------------------------------
        // ACTION PLAN
        // ----------------------------------------------------

        generateActionPlan();


        // ----------------------------------------------------
        // SCROLL TO RESULTS
        // ----------------------------------------------------

        if (results) {

            setTimeout(() => {

                results.scrollIntoView({
                    behavior: "smooth",
                    block: "start"
                });

            }, 200);
        }


    } catch (error) {

        console.error(
            "Recommendation error:",
            error
        );

        alert(
            "Unable to generate recommendation.\n\n" +
            error.message
        );

    } finally {

        const button =
            document.querySelector(
                'button[onclick="recommend()"]'
            );

        if (button) {

            button.disabled = false;

            button.textContent =
                translations[
                    $("language")?.value || "en"
                ]?.recommendation ||
                "🌱 Get Smart Recommendation";
        }
    }
}


// ------------------------------------------------------------
// CROP RECOMMENDATIONS
// ------------------------------------------------------------

function renderCropRecommendations(d) {

    const container =
        $("cropCards");

    if (!container) {
        return;
    }


    const recommendations =
        Array.isArray(d.recommendations)
            ? d.recommendations
            : [];


    if (recommendations.length === 0) {

        container.innerHTML =
            "<p>No crop recommendation available.</p>";

        return;
    }


    container.innerHTML =
        recommendations.map((item, index) => {

            const crop =
                item.crop ||
                item.name ||
                "Unknown crop";

            const confidence =
                item.confidence ??
                item.score ??
                0;

            const reason =
                item.reason ||
                "Recommended based on soil, weather and field conditions.";


            return `
                <div class="result-box">

                    <h3>
                        🌱 ${index + 1}. ${escapeHtml(crop)}
                    </h3>

                    <p>
                        <strong>Confidence:</strong>
                        ${Number(confidence).toFixed(1)}%
                    </p>

                    <p>
                        ${escapeHtml(reason)}
                    </p>

                </div>
            `;

        }).join("");
}


// ------------------------------------------------------------
// WEATHER
// ------------------------------------------------------------

function renderWeather(d) {
    const weather = d.weather || {};

    const temp =
        weather.temperature ??
        weather.temp ??
        d.temperature ??
        d.temp ??
        "N/A";

    const humidity =
        weather.humidity ??
        d.humidity ??
        "N/A";

    const rain =
        weather.rain_chance ??
        weather.rain_probability ??
        weather.precipitation_probability ??
        weather.rain ??
        d.rain_chance ??
        d.rain_probability ??
        d.precipitation_probability ??
        d.rain ??
        "N/A";

    const forecast =
        weather.forecast ??
        d.forecast ??
        "Current weather conditions available.";

    const weatherBox = document.getElementById("weather");

    if (!weatherBox) {
        return;
    }

    weatherBox.innerHTML = `

        <div class="action-item">
            <h3>🌤️ Current Weather</h3>

            <p>
                Temperature:
                <strong>${escapeHtml(String(temp))} °C</strong>
            </p>

            <p>
                Humidity:
                <strong>${escapeHtml(String(humidity))} %</strong>
            </p>

            <p>
                Rain chance:
                <strong>${escapeHtml(String(rain))} %</strong>
            </p>

            <p>
                Forecast:
                <strong>${escapeHtml(String(forecast))}</strong>
            </p>
        </div>
    `;
}

// ------------------------------------------------------------
// IRRIGATION
// ------------------------------------------------------------

function renderIrrigation(d) {

    const container =
        $("irrigation");

    if (!container) {
        return;
    }


    const irrigation =
        d.irrigation;


    if (!irrigation) {

        container.innerHTML =
            `
            <div class="result-box">
                <h3>💧 Irrigation Recommendation</h3>
                <p>
                    Irrigation recommendation is not available.
                </p>
            </div>
            `;

        return;
    }


    let text = "";


    if (typeof irrigation === "string") {

        text = irrigation;

    } else {

        text =
            irrigation.advice ||
            irrigation.text ||
            "Continue monitoring soil moisture.";

    }


    container.innerHTML = `

        <div class="result-box">

            <h3>💧 Irrigation Recommendation</h3>

            <p>
                ${escapeHtml(String(text))}
            </p>

        </div>

    `;
}


// ------------------------------------------------------------
// NUTRIENTS
// ------------------------------------------------------------

function renderNutrients(d) {

    const container =
        $("fert");

    if (!container) {
        return;
    }


    const nutrients =
        d.nutrient_advice ||
        d.nutrients ||
        d.fert ||
        {};


    let advice = [];


    if (Array.isArray(nutrients)) {

        advice = nutrients;

    } else if (Array.isArray(nutrients.advice)) {

        advice = nutrients.advice;

    } else if (Array.isArray(nutrients.text)) {

        advice = nutrients.text;

    } else if (typeof nutrients === "string") {

        advice = [nutrients];

    } else {

        // Try individual nutrient messages
        if (nutrients.nitrogen) {
            advice.push(nutrients.nitrogen);
        }

        if (nutrients.phosphorus) {
            advice.push(nutrients.phosphorus);
        }

        if (nutrients.potassium) {
            advice.push(nutrients.potassium);
        }
    }


    if (advice.length === 0) {

        container.innerHTML = `
            <div class="result-box">
                <p>
                    Nutrient recommendation is not available.
                </p>
            </div>
        `;

        return;
    }


    container.innerHTML = `

        <div class="result-box">

            ${advice.map(item => `
                <p>
                    🌱 ${escapeHtml(String(item))}
                </p>
            `).join("")}

        </div>

    `;
}


// ------------------------------------------------------------
// ALERTS
// ------------------------------------------------------------

function renderAlerts(d) {

    const container =
        $("alerts");

    if (!container) {
        return;
    }


    const alerts =
        d.alerts;


    let items = [];


    if (Array.isArray(alerts)) {

        items = alerts;

    } else if (alerts && Array.isArray(alerts.items)) {

        items = alerts.items;

    } else if (alerts && Array.isArray(alerts.text)) {

        items = alerts.text;

    } else if (typeof alerts === "string") {

        items = [alerts];
    }


    if (items.length === 0) {

        container.innerHTML = `
            <div class="result-box">
                <p>✅ No major alerts.</p>
            </div>
        `;

        return;
    }


    container.innerHTML = `

        <div class="result-box">

            ${items.map(item => `
                <p>
                    ⚠️ ${escapeHtml(String(item))}
                </p>
            `).join("")}

        </div>

    `;
}


// ------------------------------------------------------------
// DISEASE AI
// ------------------------------------------------------------

async function uploadLeaf() {

    try {

        const fileInput =
            $("leaf");

        if (!fileInput) {

            alert(
                "Leaf image input was not found."
            );

            return;
        }


        if (
            !fileInput.files ||
            fileInput.files.length === 0
        ) {

            alert(
                "Please choose a plant leaf image first."
            );

            return;
        }


        const file =
            fileInput.files[0];


        const formData =
            new FormData();

        formData.append(
            "image",
            file
        );


        const button =
            document.querySelector(
                'button[onclick="uploadLeaf()"]'
            );

        if (button) {

            button.disabled = true;

            button.textContent =
                "⏳ Analyzing...";
        }


        const response =
            await fetch(
                "/api/disease-demo",
                {
                    method: "POST",
                    body: formData
                }
            );


        const responseText =
            await response.text();

        let data;


        try {

            data =
                JSON.parse(responseText);

        } catch (error) {

            throw new Error(
                "Disease AI returned an invalid response."
            );
        }


        if (!response.ok) {

            throw new Error(
                data.error ||
                data.message ||
                "Disease analysis failed."
            );
        }


        latestDiseaseResult =
            data;


        // Show result
        const resultBox =
            $("diseaseResult");

        if (resultBox) {

            resultBox.classList.remove(
                "hidden"
            );
        }


        // Disease name
        if ($("diseaseName")) {

            $("diseaseName").textContent =
                data.disease ||
                "Unknown";
        }


        // Confidence
        if ($("diseaseConfidence")) {

            $("diseaseConfidence").textContent =
                data.confidence !== undefined
                    ? Number(data.confidence).toFixed(2) + "%"
                    : "N/A";
        }


        // Confidence level
        if ($("diseaseConfidenceLevel")) {

            $("diseaseConfidenceLevel").textContent =
                data.confidence_level ||
                "N/A";
        }


        // Treatment
        if ($("diseaseTreatment")) {

            $("diseaseTreatment").textContent =
                data.treatment ||
                "No treatment information available.";
        }


        // Prevention
        if ($("diseasePrevention")) {

            $("diseasePrevention").textContent =
                data.prevention ||
                "Continue regular crop monitoring.";
        }


        // Warning/message
        if ($("diseaseMsg")) {

            const level =
                data.confidence_level ||
                "";

            const warning =
                data.confidence_warning ||
                "";

            $("diseaseMsg").textContent =
                warning ||
                level ||
                "";
        }


        // Optional confidence bar
        if ($("confidenceFill")) {

            const confidence =
                Number(data.confidence) || 0;

            $("confidenceFill").style.width =
                Math.min(
                    100,
                    Math.max(0, confidence)
                ) + "%";
        }


        if ($("confidenceValue")) {

            const confidence =
                Number(data.confidence) || 0;

            $("confidenceValue").textContent =
                confidence.toFixed(2) + "%";
        }


        // Regenerate action plan
        generateActionPlan();


    } catch (error) {

        console.error(
            "Disease analysis error:",
            error
        );

        alert(
            "Unable to analyze leaf image.\n\n" +
            error.message
        );

    } finally {

        const button =
            document.querySelector(
                'button[onclick="uploadLeaf()"]'
            );

        if (button) {

            button.disabled = false;

            button.textContent =
                "🔍 Analyze Leaf Image";
        }
    }
}


function generateActionPlan() {

    const container = $("actionPlan");

    if (!container) return;

    if (!latestFarmResult) {
        container.innerHTML = `
            <p>🌱 Please complete the crop recommendation first.</p>
        `;
        return;
    }

    const d = latestFarmResult;

    const recommendations = Array.isArray(d.recommendations)
        ? d.recommendations
        : [];

    const weather = d.weather || {};
    const irrigation = d.irrigation || {};
    const nutrients =
        d.nutrient_advice ||
        d.nutrients ||
        d.fert ||
        {};
    const alerts = d.alerts || {};

    // --------------------------------------------------------
    // 1. CROP DECISION
    // --------------------------------------------------------

    let cropText =
        "Follow the recommended crop based on current soil, weather and field conditions.";

    if (recommendations.length > 0) {

        cropText = recommendations.map(item => {

            const crop =
                item.crop ||
                item.name ||
                "Unknown crop";

            const confidence =
                item.confidence ??
                item.score ??
                0;

            return `
                🌱 <strong>${escapeHtml(String(crop))}</strong>
                — Confidence: ${Number(confidence).toFixed(1)}%
                — Recommended based on soil, weather and field conditions.
            `;

        }).join("<br>");
    }


    // --------------------------------------------------------
    // 2. PLANT HEALTH
    // --------------------------------------------------------

    let plantHealthText =
        "Upload a clear leaf image to check plant health using Disease AI.";

    if (latestDiseaseResult) {

        const disease =
            latestDiseaseResult.disease ||
            "Unknown";

        const confidence =
            latestDiseaseResult.confidence;

        const level =
            latestDiseaseResult.confidence_level ||
            "";

        plantHealthText =
            `Disease AI result:
            <strong>${escapeHtml(String(disease))}</strong>`;

        if (confidence !== undefined) {
            plantHealthText +=
                ` — ${Number(confidence).toFixed(2)}% confidence`;
        }

        if (level) {
            plantHealthText +=
                ` — ${escapeHtml(String(level))}`;
        }
    }


    // --------------------------------------------------------
    // 3. WEATHER ACTION
    // --------------------------------------------------------

    const temp =
        weather.temperature ??
        weather.temp ??
        "N/A";

    const humidity =
        weather.humidity ??
        "N/A";

    const rain =
        weather.rain_chance ??
        weather.rain ??
        "N/A";

    const forecast =
        weather.forecast ??
        "Current weather conditions available.";

    const weatherText = `
        Current weather: ${temp} °C temperature,
        ${humidity}% humidity,
        ${rain}% rain chance.
        Forecast: ${escapeHtml(String(forecast))}
    `;


    // --------------------------------------------------------
    // 4. IRRIGATION
    // --------------------------------------------------------

    let irrigationText =
        "Monitor soil moisture before irrigation.";

    if (typeof irrigation === "string") {

        irrigationText = irrigation;

    } else {

        irrigationText =
            irrigation.advice ||
            irrigation.text ||
            "Monitor soil moisture before irrigation.";
    }


    // --------------------------------------------------------
    // 5. NUTRIENTS
    // --------------------------------------------------------

    let nutrientItems = [];

    if (Array.isArray(nutrients)) {

        nutrientItems = nutrients;

    } else if (Array.isArray(nutrients.advice)) {

        nutrientItems = nutrients.advice;

    } else if (Array.isArray(nutrients.text)) {

        nutrientItems = nutrients.text;

    } else if (typeof nutrients === "string") {

        nutrientItems = [nutrients];

    } else {

        if (nutrients.nitrogen) {
            nutrientItems.push(nutrients.nitrogen);
        }

        if (nutrients.phosphorus) {
            nutrientItems.push(nutrients.phosphorus);
        }

        if (nutrients.potassium) {
            nutrientItems.push(nutrients.potassium);
        }
    }

    let nutrientText =
        "Apply nutrients according to soil-test and crop-stage recommendations.";

    if (nutrientItems.length > 0) {

        nutrientText =
            nutrientItems
                .map(item => escapeHtml(String(item)))
                .join(" ");
    }


    // --------------------------------------------------------
    // 6. ALERTS
    // --------------------------------------------------------

    let alertItems = [];

    if (Array.isArray(alerts)) {

        alertItems = alerts;

    } else if (Array.isArray(alerts.items)) {

        alertItems = alerts.items;

    } else if (Array.isArray(alerts.text)) {

        alertItems = alerts.text;

    } else if (typeof alerts === "string") {

        alertItems = [alerts];
    }

    let alertText =
        "No major alerts.";

    if (alertItems.length > 0) {

        alertText =
            alertItems
                .map(item => escapeHtml(String(item)))
                .join(" ");
    }


    // --------------------------------------------------------
    // 7. NEXT STEPS
    // --------------------------------------------------------

    const nextSteps = [
        "Follow the recommended crop and verify suitability with local agricultural guidance.",
        "Monitor soil moisture before irrigation.",
        "Inspect leaves regularly for disease symptoms.",
        "Apply nutrients according to soil-test and crop-stage recommendations.",
        "Recheck weather conditions before irrigation or spraying."
    ];


    // --------------------------------------------------------
    // FINAL ACTION PLAN
    // --------------------------------------------------------

    container.innerHTML = `

        <div class="action-item">

            <h3>🌱 1. Crop Decision</h3>

            <p>
                ${cropText}
            </p>

        </div>


        <div class="action-item">

            <h3>🌿 2. Plant Health</h3>

            <p>
                ${plantHealthText}
            </p>

        </div>


        <div class="action-item">

            <h3>🌦️ 3. Weather-Based Action</h3>

            <p>
                ${weatherText}
            </p>

        </div>


        <div class="action-item">

            <h3>💧 4. Irrigation Action</h3>

            <p>
                <strong>Irrigation Recommendation:</strong>
                ${escapeHtml(String(irrigationText))}
            </p>

        </div>


        <div class="action-item">

            <h3>🧪 5. Nutrient Action</h3>

            <p>
                🌱 ${nutrientText}
            </p>

        </div>


        <div class="action-item">

            <h3>⚠️ 6. Risk Alerts</h3>

            <p>
                ⚠️ ${alertText}
            </p>

        </div>


        <div class="action-item">

            <h3>📋 7. Farmer's Next Steps</h3>

            <ol>
                ${nextSteps.map(step => `
                    <li>${escapeHtml(step)}</li>
                `).join("")}
            </ol>

        </div>


        <p class="action-footer">
            🖨️ Action plan generated from the Smart Crop Advisory modules.
        </p>

    `;
}


// ------------------------------------------------------------
// PRINT / SAVE REPORT
// ------------------------------------------------------------

function printReport() {

    if (!latestFarmResult) {

        alert(
            "Please generate a crop recommendation first."
        );

        return;
    }


    window.print();
}


// ------------------------------------------------------------
// HTML ESCAPE
// ------------------------------------------------------------

function escapeHtml(value) {

    return String(value)

        .replace(/&/g, "&amp;")

        .replace(/</g, "&lt;")

        .replace(/>/g, "&gt;")

        .replace(/"/g, "&quot;")

        .replace(/'/g, "&#039;");
}


// ------------------------------------------------------------
// INITIALIZE
// ------------------------------------------------------------

document.addEventListener(
    "DOMContentLoaded",
    function () {

        // Language
        if ($("language")) {

            $("language").addEventListener(
                "change",
                changeLanguage
            );

            changeLanguage();
        }


        // Print button
        const printButton =
            $("printReportBtn");

        if (printButton) {

            printButton.addEventListener(
                "click",
                printReport
            );
        }


        console.log(
            "Smart Crop Advisory frontend loaded successfully."
        );
    }
);

// =========================================
// LOAD RECOMMENDATION HISTORY
// =========================================

async function loadRecommendationHistory() {

    const tableContainer =
        document.getElementById("historyTableContainer");

    if (!tableContainer) {
        return;
    }

    try {

        const response = await fetch(
            "/api/recommendation-history"
        );

        const data = await response.json();

        if (!data.success) {

            tableContainer.innerHTML =
                "<p>Unable to load recommendation history.</p>";

            return;
        }

        const history = data.history || [];

        // Total recommendations
        const totalElement =
            document.getElementById("totalRecommendations");

        if (totalElement) {
            totalElement.textContent = data.total ?? history.length;
        }

        // No history
        if (history.length === 0) {

            tableContainer.innerHTML =
                "<p class='history-loading'>No recommendations yet.</p>";

            return;
        }

        // Latest recommendation
        const latest = history[0];

        const latestCrop =
            document.getElementById("latestCrop");

        const latestFarmer =
            document.getElementById("latestFarmer");

        const latestLocation =
            document.getElementById("latestLocation");

        const latestWeather =
            document.getElementById("latestWeather");

        if (latestCrop) {
            latestCrop.textContent =
                latest.recommended_crop || "—";
        }

        if (latestFarmer) {
            latestFarmer.textContent =
                latest.farmer_name || "—";
        }

        if (latestLocation) {
            latestLocation.textContent =
                latest.location || "—";
        }

        if (latestWeather) {
        const temperature = latest.temperature;

        const rainChance = latest.weather_rain_chance;

        if (
            temperature !== null &&
            temperature !== undefined
        ) {
            latestWeather.textContent =
                `${temperature}°C`;
        } else {
            latestWeather.textContent = "—";
        }
        }

        const summaryCrop =
        document.getElementById("summaryCrop");

        const summaryConfidence =
            document.getElementById("summaryConfidence");

        const summaryRain =
            document.getElementById("summaryRain");

        if (summaryCrop) {
            summaryCrop.textContent =
                latest.recommended_crop || "—";
        }

        if (summaryConfidence) {
            if (
                latest.confidence !== null &&
                latest.confidence !== undefined &&
                latest.confidence !== ""
            ) {
                summaryConfidence.textContent =
                    Number(latest.confidence).toFixed(1) + "%";
            } else {
                summaryConfidence.textContent = "—";
            }
        }

        if (summaryRain) {
            if (
                latest.weather_rain_chance !== null &&
                latest.weather_rain_chance !== undefined
            ) {
                summaryRain.textContent =
                    Number(latest.weather_rain_chance).toFixed(0) + "%";
            } else {
                summaryRain.textContent = "—";
            }
        }

        // Build table
        let tableHTML = `
            <table class="history-table">

                <thead>
                    <tr>
                        <th>Farmer</th>
                        <th>Location</th>
                        <th>Recommended Crop</th>
                        <th>Confidence</th>
                        <th>Date</th>
                    </tr>
                </thead>

                <tbody>
        `;

        history.forEach(function(item) {

            let confidence = item.confidence;

            if (
                confidence !== null &&
                confidence !== undefined &&
                confidence !== ""
            ) {
                confidence =
                    Number(confidence).toFixed(1) + "%";
            } else {
                confidence = "—";
            }

            tableHTML += `
                <tr>
                    <td>${escapeHtml(item.farmer_name || "—")}</td>
                    <td>${escapeHtml(item.location || "—")}</td>
                    <td>${escapeHtml(item.recommended_crop || "—")}</td>
                    <td>${confidence}</td>
                    <td>${escapeHtml(item.created_at || "—")}</td>
                </tr>
            `;
        });

        tableHTML += `
                </tbody>
            </table>
        `;

        tableContainer.innerHTML = tableHTML;

    } catch (error) {

        console.error(
            "History loading error:",
            error
        );

        tableContainer.innerHTML =
            "<p>Unable to load recommendation history.</p>";
    }

    // =========================================
    // CROP RECOMMENDATION STATISTICS
    // =========================================

    const cropStatistics =
        document.getElementById("cropStatistics");

    if (cropStatistics) {

        const cropCounts = {};

        history.forEach(function(item) {

            const crop =
                item.recommended_crop;

            if (!crop) {
                return;
            }

            cropCounts[crop] =
                (cropCounts[crop] || 0) + 1;
        });

        const cropNames =
            Object.keys(cropCounts);

        if (cropNames.length === 0) {

            cropStatistics.innerHTML =
                "<p class='history-loading'>No crop statistics available yet.</p>";

        } else {

            cropNames.sort(function(a, b) {
                return cropCounts[b] - cropCounts[a];
            });

            let statisticsHTML = "";

            cropNames.forEach(function(crop) {

                statisticsHTML += `
                    <div class="crop-stat-row">

                        <span class="crop-stat-name">
                            🌾 ${escapeHtml(crop)}
                        </span>

                        <span class="crop-stat-count">
                            ${cropCounts[crop]} recommendation(s)
                        </span>

                    </div>
                `;
            });

            cropStatistics.innerHTML =
                statisticsHTML;
        }
    }
}

document.addEventListener("DOMContentLoaded", function () {
    loadRecommendationHistory();
});

// =========================================
// REFRESH HISTORY
// =========================================

async function refreshRecommendationHistory() {

    const button =
        document.getElementById("refreshHistoryBtn");

    if (!button) {
        return;
    }

    button.textContent = "⏳ Refreshing...";
    button.disabled = true;

    try {

        await loadRecommendationHistory();

    } catch (error) {

        console.error(
            "Refresh History Error:",
            error
        );

    }

    button.textContent = "🔄 Refresh History";
    button.disabled = false;
}

// Make function available to HTML
window.refreshRecommendationHistory =
    refreshRecommendationHistory;

// =========================================
// DASHBOARD LANGUAGE SUPPORT
// =========================================

document.addEventListener("DOMContentLoaded", function () {

    const languageElement =
        document.getElementById("language");

    if (!languageElement) {
        return;
    }

    function updateDashboardLanguage() {

        const selected =
            languageElement.value;

        const dashboardText = {

            English: {
                title: "📊 Smart Farming Dashboard",
                subtitle: "Recent crop recommendation history",
                recent: "📋 Recent Recommendations",
                statistics: "📊 Crop Recommendation Statistics"
            },

            Kannada: {
                title: "📊 ಸ್ಮಾರ್ಟ್ ಕೃಷಿ ಡ್ಯಾಶ್‌ಬೋರ್ಡ್",
                subtitle: "ಇತ್ತೀಚಿನ ಬೆಳೆ ಶಿಫಾರಸುಗಳ ಇತಿಹಾಸ",
                recent: "📋 ಇತ್ತೀಚಿನ ಶಿಫಾರಸುಗಳು",
                statistics: "📊 ಬೆಳೆ ಶಿಫಾರಸುಗಳ ಅಂಕಿಅಂಶಗಳು"
            },

            Hindi: {
                title: "📊 स्मार्ट कृषि डैशबोर्ड",
                subtitle: "हाल की फसल सिफारिशों का इतिहास",
                recent: "📋 हाल की सिफारिशें",
                statistics: "📊 फसल सिफारिश के आँकड़े"
            }

        };

        const text =
            dashboardText[selected] ||
            dashboardText.English;

        const title =
            document.getElementById("dashboardTitle");

        const subtitle =
            document.getElementById("dashboardSubtitle");

        const recent =
            document.getElementById("recentRecommendationsTitle");

        const statistics =
            document.getElementById("cropStatisticsTitle");

        if (title) {
            title.textContent = text.title;
        }

        if (subtitle) {
            subtitle.textContent = text.subtitle;
        }

        if (recent) {
            recent.textContent = text.recent;
        }

        if (statistics) {
            statistics.textContent = text.statistics;
        }
    }

    languageElement.addEventListener(
        "change",
        updateDashboardLanguage
    );

    updateDashboardLanguage();
});

// =========================================
// SYSTEM STATUS LANGUAGE SUPPORT
// =========================================

document.addEventListener("DOMContentLoaded", function () {

    const languageElement =
        document.getElementById("language");

    if (!languageElement) {
        return;
    }

    function updateSystemStatusLanguage() {

        const selected = languageElement.value;

        const statusText = {

            English: {
                title: "🟢 System Status: Online",
                weather: "🌦️ Live Weather",
                crop: "🤖 Crop AI",
                disease: "🦠 Disease AI",
                database: "💾 Database"
            },

            Kannada: {
                title: "🟢 ಸಿಸ್ಟಮ್ ಸ್ಥಿತಿ: ಆನ್‌ಲೈನ್",
                weather: "🌦️ ಲೈವ್ ಹವಾಮಾನ",
                crop: "🤖 ಬೆಳೆ AI",
                disease: "🦠 ಸಸ್ಯ ರೋಗ AI",
                database: "💾 ಡೇಟಾಬೇಸ್"
            },

            Hindi: {
                title: "🟢 सिस्टम स्थिति: ऑनलाइन",
                weather: "🌦️ लाइव मौसम",
                crop: "🤖 फसल AI",
                disease: "🦠 पौधों की बीमारी AI",
                database: "💾 डेटाबेस"
            }

        };

        const text =
            statusText[selected] ||
            statusText.English;

        const title =
            document.getElementById("systemStatusTitle");

        const weather =
            document.getElementById("liveWeatherStatus");

        const crop =
            document.getElementById("cropAIStatus");

        const disease =
            document.getElementById("diseaseAIStatus");

        const database =
            document.getElementById("databaseStatus");

        if (title) {
            title.textContent = text.title;
        }

        if (weather) {
            weather.textContent = text.weather;
        }

        if (crop) {
            crop.textContent = text.crop;
        }

        if (disease) {
            disease.textContent = text.disease;
        }

        if (database) {
            database.textContent = text.database;
        }
    }

    languageElement.addEventListener(
        "change",
        updateSystemStatusLanguage
    );

    updateSystemStatusLanguage();
});