from flask import Flask, render_template, request, jsonify
import os
import json
import sqlite3
from datetime import datetime

import numpy as np
import pandas as pd
import requests
import joblib
import tensorflow as tf
from PIL import Image

# ----------------------------------------------------
# Project paths and database
# ----------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DB = os.path.join(
    BASE_DIR,
    "smart_crop.db"
)


# ============================================================
# SMART CROP ADVISORY SYSTEM
# ============================================================

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_DIR = os.path.join(BASE_DIR, "model")
DATABASE_PATH = os.path.join(BASE_DIR, "farmers.db")

CROP_MODEL_PATH = os.path.join(MODEL_DIR, "crop_model.pkl")
DISEASE_MODEL_PATH = os.path.join(MODEL_DIR, "plant_disease_model.keras")
DISEASE_CLASSES_PATH = os.path.join(
    MODEL_DIR,
    "plant_disease_classes.json"
)

UPLOAD_FOLDER = "/tmp/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024


# ============================================================
# MODEL FEATURES
# ============================================================

MODEL_FEATURES = [
    "N",
    "P",
    "K",
    "temperature",
    "humidity",
    "ph",
    "rainfall"
]


# ============================================================
# LOAD CROP MODEL
# ============================================================

crop_model = None

try:
    if os.path.exists(CROP_MODEL_PATH):
        crop_model = joblib.load(CROP_MODEL_PATH)
        print("ML crop model loaded successfully!")
    else:
        print("WARNING: Crop model not found:")
        print(CROP_MODEL_PATH)
except Exception as e:
    print("ERROR loading crop model:", e)


# ============================================================
# LOAD PLANT DISEASE MODEL
# ============================================================

disease_model = None
disease_classes = []

try:
    if os.path.exists(DISEASE_MODEL_PATH):
        disease_model = tf.keras.models.load_model(
            DISEASE_MODEL_PATH
        )

    if os.path.exists(DISEASE_CLASSES_PATH):
        with open(
            DISEASE_CLASSES_PATH,
            "r",
            encoding="utf-8"
        ) as f:
            disease_classes = json.load(f)

    print("Plant Disease AI loaded successfully!")
    print("Number of classes:", len(disease_classes))

except Exception as e:
    print("ERROR loading Plant Disease AI:", e)


# ============================================================
# DATABASE
# ============================================================
def init_database():
    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS farmers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            location TEXT,
            land_area REAL,
            soil_type TEXT,
            water_availability TEXT,
            language TEXT,
            nitrogen REAL,
            phosphorus REAL,
            potassium REAL,
            soil_ph REAL,
            soil_moisture REAL,
            expected_rainfall REAL,
            temperature REAL,
            created_at TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS recommendation_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            farmer_name TEXT,
            location TEXT,
            recommended_crop TEXT,
            confidence REAL,
            nitrogen REAL,
            phosphorus REAL,
            potassium REAL,
            soil_ph REAL,
            soil_moisture REAL,
            rainfall REAL,
            temperature REAL,
            weather_rain_chance REAL,
            created_at TEXT
        )
    """)

    connection.commit()
    connection.close()


init_database()


# ============================================================
# GENERAL HELPERS
# ============================================================

def clean_text(value, default=""):
    if value is None:
        return default

    return str(value).strip()


def get_number(data, *keys, default=None):
    """
    Safely get a numeric value.

    Accepts multiple possible field names so the frontend
    can use either camelCase or lowercase names.
    """

    for key in keys:
        if key not in data:
            continue

        value = data.get(key)

        if value is None:
            continue

        if isinstance(value, str):
            value = value.strip()

            if value == "":
                continue

        try:
            return float(value)
        except (ValueError, TypeError):
            continue

    return default


def clamp(value, minimum, maximum):
    return max(minimum, min(maximum, value))


def format_crop_name(name):
    if not name:
        return "Unknown crop"

    name = str(name)

    replacements = {
        "_": " ",
        "(": "(",
        ")": ")"
    }

    for old, new in replacements.items():
        name = name.replace(old, new)

    return " ".join(name.split()).title()


def format_disease_name(name):
    if not name:
        return "Unknown"

    name = str(name)

    parts = name.split("___")

    if len(parts) == 2:
        crop = parts[0].replace("_", " ")
        condition = parts[1].replace("_", " ")

        crop = " ".join(crop.split()).title()
        condition = " ".join(condition.split()).lower()

        return f"{crop} — {condition}"

    return name.replace("_", " ").title()


# ============================================================
# DISEASE ADVICE
# ============================================================

def get_disease_advice(disease_name):
    name = str(disease_name).lower()

    if "healthy" in name:
        return {
            "treatment": (
                "No disease detected. Continue normal crop care."
            ),
            "prevention": (
                "Continue regular crop monitoring and maintain "
                "good field hygiene."
            )
        }

    if "blight" in name:
        return {
            "treatment": (
                "Remove badly affected leaves and avoid overhead "
                "irrigation. Follow locally approved disease-control "
                "guidance."
            ),
            "prevention": (
                "Maintain field sanitation, avoid prolonged leaf "
                "wetness, and provide good plant spacing."
            )
        }

    if "rust" in name:
        return {
            "treatment": (
                "Remove severely affected plant material and follow "
                "locally approved fungicide guidance when required."
            ),
            "prevention": (
                "Improve air circulation, avoid excessive leaf "
                "wetness, and monitor plants regularly."
            )
        }

    if "mildew" in name:
        return {
            "treatment": (
                "Remove severely affected leaves and improve air "
                "circulation. Follow local agricultural guidance."
            ),
            "prevention": (
                "Avoid excessive humidity around foliage and "
                "monitor plants frequently."
            )
        }

    if "spot" in name:
        return {
            "treatment": (
                "Remove severely affected leaves and dispose of "
                "infected plant material safely."
            ),
            "prevention": (
                "Keep foliage dry where possible, maintain spacing, "
                "and avoid unnecessary overhead irrigation."
            )
        }

    return {
        "treatment": (
            "Follow local agricultural guidance and inspect the "
            "plant carefully before applying any treatment."
        ),
        "prevention": (
            "Maintain good field hygiene, suitable spacing, and "
            "regular crop monitoring."
        )
    }


# ============================================================
# OPEN-METEO GEOCODING
# ============================================================

def geocode_location(location):
    location = clean_text(location)

    if not location:
        return None

    try:
        url = "https://geocoding-api.open-meteo.com/v1/search"

        params = {
            "name": location,
            "count": 1,
            "language": "en",
            "format": "json"
        }

        response = requests.get(
            url,
            params=params,
            timeout=10
        )

        response.raise_for_status()

        data = response.json()

        results = data.get("results", [])

        if not results:
            return None

        result = results[0]

        return {
            "latitude": result.get("latitude"),
            "longitude": result.get("longitude"),
            "name": result.get("name"),
            "country": result.get("country"),
            "admin1": result.get("admin1")
        }

    except Exception as e:
        print("Geocoding error:", e)
        return None


# ============================================================
# LIVE WEATHER
# ============================================================

def get_live_weather(location):
    """
    Gets current weather and today's precipitation probability
    using Open-Meteo.
    """

    coordinates = geocode_location(location)

    if not coordinates:
        return {
            "success": False,
            "message": "Unable to find the specified location."
        }

    latitude = coordinates["latitude"]
    longitude = coordinates["longitude"]

    try:
        url = "https://api.open-meteo.com/v1/forecast"

        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": (
                "temperature_2m,"
                "relative_humidity_2m,"
                "precipitation,"
                "weather_code"
            ),
            "daily": (
                "precipitation_probability_max,"
                "precipitation_sum"
            ),
            "timezone": "auto",
            "forecast_days": 1
        }

        response = requests.get(
            url,
            params=params,
            timeout=10
        )

        response.raise_for_status()

        data = response.json()

        current = data.get("current", {})
        daily = data.get("daily", {})

        temperature = current.get("temperature_2m")
        humidity = current.get("relative_humidity_2m")

        rain_probability_list = daily.get(
            "precipitation_probability_max",
            [0]
        )

        rain_amount_list = daily.get(
            "precipitation_sum",
            [0]
        )

        rain_probability = (
            rain_probability_list[0]
            if rain_probability_list
            else 0
        )

        rain_amount = (
            rain_amount_list[0]
            if rain_amount_list
            else 0
        )

        return {
            "success": True,
            "location": coordinates["name"],
            "country": coordinates["country"],
            "temperature": (
                round(float(temperature), 1)
                if temperature is not None
                else None
            ),
            "humidity": (
                round(float(humidity), 1)
                if humidity is not None
                else None
            ),
            "rain_probability": (
                round(float(rain_probability), 1)
            ),
            "rain_amount": (
                round(float(rain_amount), 1)
            ),
            "weather_code": current.get("weather_code")
        }

    except Exception as e:
        print("Weather API error:", e)

        return {
            "success": False,
            "message": "Live weather could not be retrieved."
        }


# ============================================================
# WEATHER FALLBACK
# ============================================================

def weather_fallback(user_temperature):
    temperature = (
        user_temperature
        if user_temperature is not None
        else 25.0
    )

    return {
        "success": False,
        "temperature": round(float(temperature), 1),
        "humidity": 60.0,
        "rain_probability": 20.0,
        "rain_amount": 0.0,
        "location": "User supplied location",
        "message": "Using user-provided weather values."
    }


# ============================================================
# IRRIGATION ADVISORY
# ============================================================

def create_irrigation_advice(
    soil_moisture,
    rain_probability,
    rain_amount
):

    moisture = float(soil_moisture)

    if rain_probability >= 70 or rain_amount >= 10:
        return (
            "Rain is likely today. Delay irrigation if the soil "
            "already has adequate moisture and avoid waterlogging."
        )

    if moisture < 25:
        return (
            "Soil moisture is low. Irrigate soon using an efficient "
            "method such as drip irrigation, if available."
        )

    if moisture < 45:
        return (
            "Soil moisture is moderate. Monitor the field and "
            "irrigate when moisture drops further."
        )

    if moisture < 70:
        return (
            "Soil moisture is good. Avoid unnecessary irrigation "
            "and continue monitoring."
        )

    return (
        "Soil moisture is high. Avoid irrigation until the soil "
        "drains sufficiently."
    )


# ============================================================
# NUTRIENT ADVISORY
# ============================================================

def create_nutrient_advice(nitrogen, phosphorus, potassium):

    advice = []

    # Approximate advisory thresholds.
    # These are not a replacement for laboratory soil testing.

    if nitrogen < 50:
        advice.append(
            "Nitrogen appears low; confirm with a soil test before "
            "nutrient application."
        )
    elif nitrogen > 140:
        advice.append(
            "Nitrogen appears high; avoid unnecessary nitrogen "
            "application and confirm with a soil test."
        )
    else:
        advice.append(
            "Nitrogen level appears adequate."
        )

    if phosphorus < 30:
        advice.append(
            "Phosphorus appears low; consider soil-test-based "
            "nutrient management."
        )
    elif phosphorus > 100:
        advice.append(
            "Phosphorus appears high; avoid excessive application."
        )
    else:
        advice.append(
            "Phosphorus level appears adequate."
        )

    if potassium < 30:
        advice.append(
            "Potassium appears low; confirm with a soil test before "
            "application."
        )
    elif potassium > 200:
        advice.append(
            "Potassium appears high; avoid unnecessary application."
        )
    else:
        advice.append(
            "Potassium level appears adequate."
        )

    return advice


# ============================================================
# ALERT GENERATION
# ============================================================

def create_alerts(
    temperature,
    humidity,
    rain_probability,
    soil_moisture
):

    alerts = []

    if temperature >= 35:
        alerts.append(
            "High temperature risk. Check crop water requirements "
            "and monitor plants for heat stress."
        )

    if temperature <= 10:
        alerts.append(
            "Low temperature risk. Monitor sensitive crops for "
            "cold stress."
        )

    if humidity >= 80:
        alerts.append(
            "High humidity may increase fungal disease risk. "
            "Inspect leaves regularly and improve air circulation."
        )

    if rain_probability >= 70:
        alerts.append(
            "High chance of rain. Consider delaying irrigation "
            "and unnecessary spraying."
        )

    if soil_moisture < 25:
        alerts.append(
            "Low soil moisture detected. Irrigation may be required."
        )

    if soil_moisture > 80:
        alerts.append(
            "Very high soil moisture. Avoid over-irrigation."
        )

    if not alerts:
        alerts.append(
            "No major weather or soil-moisture alert in the "
            "current conditions."
        )

    return alerts


# ============================================================
# CROP RECOMMENDATION
# ============================================================

def predict_crops(
    nitrogen,
    phosphorus,
    potassium,
    temperature,
    humidity,
    ph,
    rainfall
):

    if crop_model is None:
        raise RuntimeError(
            "Crop ML model is not loaded."
        )

    values = {
        "N": float(nitrogen),
        "P": float(phosphorus),
        "K": float(potassium),
        "temperature": float(temperature),
        "humidity": float(humidity),
        "ph": float(ph),
        "rainfall": float(rainfall)
    }

    dataframe = pd.DataFrame(
        [values],
        columns=MODEL_FEATURES
    )

    # --------------------------------------------------------
    # If Random Forest supports probabilities
    # --------------------------------------------------------

    if hasattr(crop_model, "predict_proba"):

        probabilities = crop_model.predict_proba(dataframe)[0]

        classes = list(crop_model.classes_)

        ranked = sorted(
            zip(classes, probabilities),
            key=lambda x: x[1],
            reverse=True
        )

        results = []

        for crop, probability in ranked[:3]:

            confidence = round(
                float(probability) * 100,
                1
            )

            results.append({
                "crop": format_crop_name(crop),
                "raw_crop": str(crop),
                "confidence": confidence,
                "score": confidence,
                "reason": (
                    "Recommended based on soil, weather and "
                    "field conditions."
                )
            })

        return results

    # --------------------------------------------------------
    # Fallback if model has no predict_proba
    # --------------------------------------------------------

    prediction = crop_model.predict(dataframe)

    crop = prediction[0]

    return [{
        "crop": format_crop_name(crop),
        "raw_crop": str(crop),
        "confidence": 100.0,
        "score": 100.0,
        "reason": (
            "Recommended based on soil, weather and "
            "field conditions."
        )
    }]


# ============================================================
# HOME PAGE
# ============================================================

@app.route("/")
def index():
    return render_template("index.html")


# ============================================================
# HEALTH CHECK
# ============================================================

@app.route("/api/health", methods=["GET"])
def health():

    return jsonify({
        "success": True,
        "crop_model_loaded": crop_model is not None,
        "disease_model_loaded": disease_model is not None,
        "disease_classes": len(disease_classes),
        "message": "Smart Crop Advisory System is running."
    })


# ============================================================
# WEATHER API
# ============================================================

@app.route("/api/weather", methods=["POST"])
def weather_api():

    try:
        data = request.get_json(
            silent=True
        ) or {}

        location = clean_text(
            data.get("location")
            or data.get("place")
        )

        temperature = get_number(
            data,
            "temperature",
            "temp",
            default=25
        )

        if location:
            weather = get_live_weather(location)

            if weather.get("success"):
                return jsonify(weather)

        return jsonify(
            weather_fallback(temperature)
        )

    except Exception as e:
        print("Weather endpoint error:", e)

        return jsonify({
            "success": False,
            "message": "Weather service error."
        }), 500

def save_recommendation_history(
    farmer_name,
    location,
    recommended_crop,
    confidence,
    nitrogen,
    phosphorus,
    potassium,
    soil_ph,
    soil_moisture,
    rainfall,
    temperature,
    weather_rain_chance
):
    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO recommendation_history (
            farmer_name,
            location,
            recommended_crop,
            confidence,
            nitrogen,
            phosphorus,
            potassium,
            soil_ph,
            soil_moisture,
            rainfall,
            temperature,
            weather_rain_chance,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
    """, (
        farmer_name,
        location,
        recommended_crop,
        confidence,
        nitrogen,
        phosphorus,
        potassium,
        soil_ph,
        soil_moisture,
        rainfall,
        temperature,
        weather_rain_chance
    ))

    connection.commit()
    connection.close()

# ============================================================
# RECOMMENDATION API
# ============================================================

@app.route("/api/recommend", methods=["POST"])
def recommend():

    try:

        # ----------------------------------------------------
        # Read JSON safely
        # ----------------------------------------------------

        data = request.get_json(silent=True)

        if not data:
            data = request.form.to_dict()

        if not data:
            return jsonify({
                "success": False,
                "error": "No form data was received."
            }), 400

        print("\n==============================")
        print("RECOMMENDATION REQUEST")
        print("==============================")
        print(data)

        # ----------------------------------------------------
        # FARMER INFORMATION
        # ----------------------------------------------------

        farmer_name = clean_text(
            data.get("name") or data.get("farmerName")
        )

        location = clean_text(
            data.get("location") or data.get("place")
        )

        land_area = get_number(
            data,
            "landArea",
            "land_area",
            "area",
            default=0
        )

        soil_type = clean_text(
            data.get("soilType") or data.get("soil_type")
        )

        water_availability = clean_text(
            data.get("water")
            or data.get("waterAvailability")
            or data.get("water_availability")
        )

        language = clean_text(
            data.get("language"),
            "English"
        )

        # ----------------------------------------------------
        # SOIL NUTRIENTS
        # ----------------------------------------------------

        nitrogen = get_number(
            data,
            "N",
            "n",
            "nitrogen",
            "Nitrogen",
            "nitrogenValue",
            "nitrogen_value"
        )

        phosphorus = get_number(
            data,
            "P",
            "p",
            "phosphorus",
            "Phosphorus",
            "phosphorusValue",
            "phosphorus_value"
        )

        potassium = get_number(
            data,
            "K",
            "k",
            "potassium",
            "Potassium",
            "potassiumValue",
            "potassium_value"
        )

        # ----------------------------------------------------
        # OTHER FIELD CONDITIONS
        # ----------------------------------------------------

        soil_ph = get_number(
            data,
            "ph",
            "pH",
            "soilPH",
            "soil_ph",
            "soilPh"
        )

        soil_moisture = get_number(
            data,
            "moisture",
            "soilMoisture",
            "soil_moisture",
            "soilMoisturePercent",
            default=50
        )

        expected_rainfall = get_number(
            data,
            "rainfall",
            "expectedRainfall",
            "expected_rainfall",
            default=100
        )

        user_temperature = get_number(
            data,
            "temperature",
            "temp",
            default=25
        )

        # ----------------------------------------------------
        # DEBUG VALUES
        # ----------------------------------------------------

        print("\nReceived soil values:")
        print("Nitrogen:", nitrogen)
        print("Phosphorus:", phosphorus)
        print("Potassium:", potassium)
        print("Soil pH:", soil_ph)
        print("Soil moisture:", soil_moisture)
        print("Expected rainfall:", expected_rainfall)
        print("Temperature:", user_temperature)

        # ----------------------------------------------------
        # VALIDATION
        # ----------------------------------------------------

        missing = []

        if nitrogen is None:
            missing.append("Nitrogen (N)")

        if phosphorus is None:
            missing.append("Phosphorus (P)")

        if potassium is None:
            missing.append("Potassium (K)")

        if soil_ph is None:
            missing.append("Soil pH")

        if missing:
            return jsonify({
                "success": False,
                "error": (
                    "Soil nutrient/field values were not received: "
                    + ", ".join(missing)
                ),
                "missing": missing
            }), 400

        # ----------------------------------------------------
        # RANGE SAFETY
        # ----------------------------------------------------

        nitrogen = clamp(nitrogen, 0, 500)
        phosphorus = clamp(phosphorus, 0, 500)
        potassium = clamp(potassium, 0, 500)
        soil_ph = clamp(soil_ph, 0, 14)
        soil_moisture = clamp(soil_moisture, 0, 100)
        expected_rainfall = max(0, expected_rainfall)
        user_temperature = clamp(user_temperature, -20, 60)

        # ----------------------------------------------------
        # LIVE WEATHER
        # ----------------------------------------------------

        live_weather = None

        if location:
            live_weather = get_live_weather(location)

        if not live_weather or not live_weather.get("success"):
            live_weather = weather_fallback(user_temperature)

        weather_temperature = (
            live_weather.get("temperature")
            if live_weather.get("temperature") is not None
            else user_temperature
        )

        weather_humidity = (
            live_weather.get("humidity")
            if live_weather.get("humidity") is not None
            else 60
        )

        rain_probability = live_weather.get(
            "rain_probability",
            20
        )

        rain_amount = live_weather.get(
            "rain_amount",
            0
        )

        # ----------------------------------------------------
        # ML CROP PREDICTION
        # ----------------------------------------------------

        crop_results = predict_crops(
            nitrogen=nitrogen,
            phosphorus=phosphorus,
            potassium=potassium,
            temperature=weather_temperature,
            humidity=weather_humidity,
            ph=soil_ph,
            rainfall=expected_rainfall
        )

        # ----------------------------------------------------
        # IRRIGATION
        # ----------------------------------------------------

        irrigation = create_irrigation_advice(
            soil_moisture,
            rain_probability,
            rain_amount
        )

        # ----------------------------------------------------
        # NUTRIENTS
        # ----------------------------------------------------

        nutrient_advice = create_nutrient_advice(
            nitrogen,
            phosphorus,
            potassium
        )

        # ----------------------------------------------------
        # ALERTS
        # ----------------------------------------------------

        alerts = create_alerts(
            weather_temperature,
            weather_humidity,
            rain_probability,
            soil_moisture
        )

        # ----------------------------------------------------
        # HUMAN-READABLE WEATHER
        # ----------------------------------------------------

        weather_text = (
            f"Current Weather Temperature: "
            f"{weather_temperature} °C "
            f"Humidity: {weather_humidity} % "
            f"Rain chance: {rain_probability} %"
        )

        # ----------------------------------------------------
        # RESPONSE
        # ----------------------------------------------------

        response = {
            "success": True,

            "farmer": {
                "name": farmer_name,
                "location": location,
                "land_area": land_area,
                "soil_type": soil_type,
                "water_availability": water_availability,
                "language": language
            },

            "soil": {
                "N": nitrogen,
                "P": phosphorus,
                "K": potassium,
                "ph": soil_ph,
                "moisture": soil_moisture,
                "rainfall": expected_rainfall
            },

            "weather": {
                "temperature": weather_temperature,
                "humidity": weather_humidity,
                "rain_probability": rain_probability,
                "rain_amount": rain_amount,
                "location": live_weather.get(
                    "location",
                    location
                ),
                "text": weather_text,
                "live": live_weather.get(
                    "success",
                    False
                )
            },

            "crops": crop_results,

            "recommendations": crop_results,
            "crop_recommendations": crop_results,

            "irrigation": {
                "advice": irrigation,
                "text": irrigation,
                "soil_moisture": soil_moisture
            },

            "nutrients": {
                "advice": nutrient_advice,
                "text": nutrient_advice
            },

            "fertilizer": {
                "advice": nutrient_advice,
                "text": nutrient_advice
            },

            "alerts": {
                "items": alerts,
                "text": alerts
            },

            "message": (
                "Crop recommendations generated successfully."
            )
        }

        # ----------------------------------------------------
        # SAVE RECOMMENDATION HISTORY
        # ----------------------------------------------------

        try:

            recommended_crop = ""
            confidence = 0

            if crop_results:

                first_crop = crop_results[0]

                if isinstance(first_crop, dict):

                    recommended_crop = (
                        first_crop.get("crop")
                        or first_crop.get("name")
                        or first_crop.get("label")
                        or first_crop.get("recommended_crop")
                        or ""
                    )

                    confidence = (
                        first_crop.get("confidence")
                        or first_crop.get("probability")
                        or first_crop.get("score")
                        or 0
                    )

                elif isinstance(first_crop, str):

                    recommended_crop = first_crop

            connection = sqlite3.connect(DATABASE_PATH)
            cursor = connection.cursor()

            cursor.execute("""
                INSERT INTO recommendation_history (
                    farmer_name,
                    location,
                    recommended_crop,
                    confidence,
                    nitrogen,
                    phosphorus,
                    potassium,
                    soil_ph,
                    soil_moisture,
                    rainfall,
                    temperature,
                    weather_rain_chance,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
            """, (
                farmer_name,
                location,
                recommended_crop,
                confidence,
                nitrogen,
                phosphorus,
                potassium,
                soil_ph,
                soil_moisture,
                expected_rainfall,
                weather_temperature,
                rain_probability
            ))

            connection.commit()
            connection.close()

            print("Recommendation history saved successfully!")

        except Exception as history_error:

            print(
                "History save warning:",
                type(history_error).__name__,
                str(history_error)
            )

        # ----------------------------------------------------
        # FINAL RESPONSE
        # ----------------------------------------------------

        # SAVE RECOMMENDATION HISTORY

        if crop_results:

            top_crop = crop_results[0]

            recommended_crop = top_crop.get("crop", "Unknown")

            confidence = top_crop.get("confidence", 0)

            save_recommendation_history(
                farmer_name,
                location,
                recommended_crop,
                confidence,
                nitrogen,
                phosphorus,
                potassium,
                soil_ph,
                soil_moisture,
                expected_rainfall,
                weather_temperature,
                rain_probability
            )

        print("\nRecommendation successful!")
        print("Crops:", crop_results)

        return jsonify(response)
    except Exception as e:

        print("\n==============================")
        print("RECOMMENDATION ERROR")
        print("==============================")
        print(type(e).__name__, str(e))

        return jsonify({
            "success": False,
            "error": "Unable to generate recommendation.",
            "details": str(e)
        }), 500


# ============================================================
# SAVE FARMER PROFILE
# ============================================================

@app.route("/api/save-farmer", methods=["POST"])
def save_farmer():
    try:
        # Accept JSON from JavaScript OR normal form data
        d = request.get_json(silent=True) or request.form.to_dict()

        name = d.get("name", "").strip()
        location = d.get("location", "").strip()

        land_area = d.get("land_area", 0)

        soil_type = (
            d.get("soil_type")
            or d.get("soilType")
            or ""
        )

        water = (
            d.get("water_availability")
            or d.get("water")
            or ""
        )

        language = d.get("language", "English")

        # Validate required fields
        if not name:
            return jsonify({
                "success": False,
                "error": "Farmer name is required."
            }), 400

        if not location:
            return jsonify({
                "success": False,
                "error": "Location is required."
            }), 400

        try:
            land_area = float(land_area)
        except (TypeError, ValueError):
            land_area = 0

        # Save to database
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO farmers
            (
                name,
                location,
                land_area,
                soil_type,
                water_availability,
                language,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            name,
            location,
            land_area,
            soil_type,
            water,
            language,
            datetime.now().isoformat()
        ))

        conn.commit()

        farmer_id = cursor.lastrowid

        conn.close()

        print("\nFarmer profile saved:")
        print("ID:", farmer_id)
        print("Name:", name)
        print("Location:", location)

        return jsonify({
            "success": True,
            "message": "Farmer profile saved successfully.",
            "farmer_id": farmer_id
        })

    except Exception as e:

        print("\nFarmer profile error:")
        print(type(e).__name__, str(e))

        return jsonify({
            "success": False,
            "error": "Unable to save farmer profile.",
            "details": str(e)
        }), 500

# ============================================================
# PLANT DISEASE AI
# ============================================================

@app.route("/api/disease-demo", methods=["POST"])
def disease_demo():

    try:

        # ----------------------------------------------------
        # Check model
        # ----------------------------------------------------

        if disease_model is None:

            return jsonify({
                "success": False,
                "error": (
                    "Plant Disease AI model is not loaded."
                )
            }), 500

        # ----------------------------------------------------
        # Check image
        # ----------------------------------------------------

        if "image" not in request.files:

            return jsonify({
                "success": False,
                "error": (
                    "Please upload a leaf image."
                )
            }), 400

        file = request.files["image"]

        if not file or not file.filename:

            return jsonify({
                "success": False,
                "error": (
                    "Please select an image file."
                )
            }), 400

        # ----------------------------------------------------
        # Open image
        # ----------------------------------------------------

        image = Image.open(
            file.stream
        ).convert("RGB")

        # IMPORTANT:
        # Your trained model expects 160 x 160.
        image = image.resize(
            (160, 160)
        )

        image_array = np.array(
            image,
            dtype=np.float32
        )

        image_array = image_array / 255.0

        image_array = np.expand_dims(
            image_array,
            axis=0
        )

        # ----------------------------------------------------
        # Prediction
        # ----------------------------------------------------

        prediction = disease_model.predict(
            image_array,
            verbose=0
        )[0]

        predicted_index = int(
            np.argmax(prediction)
        )

        confidence = float(
            prediction[predicted_index]
        ) * 100

        # ----------------------------------------------------
        # Class name
        # ----------------------------------------------------

        if (
            predicted_index < len(disease_classes)
        ):
            raw_disease = disease_classes[
                predicted_index
            ]
        else:
            raw_disease = "Unknown"

        # ----------------------------------------------------
        # Confidence levels
        # ----------------------------------------------------

        if confidence >= 80:

            confidence_level = (
                "High confidence"
            )

            confidence_warning = (
                "AI is reasonably confident in this prediction."
            )

        elif confidence >= 60:

            confidence_level = (
                "Moderate confidence"
            )

            confidence_warning = (
                "Please verify the result with a clear image "
                "or local agricultural expert."
            )

        else:

            confidence_level = (
                "Low confidence"
            )

            confidence_warning = (
                "Low confidence. Please upload a clearer "
                "leaf image for better analysis."
            )

        # ----------------------------------------------------
        # Uncertain prediction
        # ----------------------------------------------------

        # ----------------------------------------------------
        # Confidence level
        # ----------------------------------------------------

        if confidence >= 80:
            confidence_level = "High confidence"
            confidence_warning = (
                "AI is reasonably confident in this prediction."
            )

        elif confidence >= 60:
            confidence_level = "Moderate confidence"
            confidence_warning = (
                "Please verify the result with a clear image "
                "or a local agricultural expert."
            )

        else:
            confidence_level = "Low confidence"
            confidence_warning = (
                "Low confidence. Please upload a clearer leaf image "
                "or verify with a local agricultural expert."
            )


        # ----------------------------------------------------
        # Disease name and advice
        # ----------------------------------------------------

        display_disease = format_disease_name(raw_disease)

        advice = get_disease_advice(raw_disease)

        treatment = advice["treatment"]

        prevention = advice["prevention"]


        # ----------------------------------------------------
        # Response
        # ----------------------------------------------------

        result = {
            "success": True,

            "disease": display_disease,

            "raw_disease": raw_disease,

            "confidence": round(
                confidence,
                2
            ),

            "confidence_level": confidence_level,

            "confidence_warning": confidence_warning,

            "treatment": treatment,

            "prevention": prevention
        }


        print("\nDisease prediction:")
        print("Disease:", display_disease)
        print("Confidence:", confidence)
        print("Confidence level:", confidence_level)


        return jsonify(result)
    except Exception as e:

        print("Disease prediction error:", e)

        return jsonify({
            "success": False,
            "error": (
                "Unable to process the image for disease prediction."
            ),
            "details": str(e)
        }), 500
def disease_alias():

    return disease_demo()


# ============================================================
# 404 HANDLER FOR API
# ============================================================

@app.errorhandler(404)
def page_not_found(error):

    if request.path.startswith("/api/"):

        return jsonify({
            "success": False,
            "error": "API endpoint not found.",
            "path": request.path
        }), 404

    return error


# ============================================================
# FILE SIZE ERROR
# ============================================================

@app.errorhandler(413)
def file_too_large(error):

    return jsonify({
        "success": False,
        "error": (
            "Image is too large. Maximum allowed size is 10 MB."
        )
    }), 413


# ============================================================
# START SERVER
# ============================================================
@app.route("/api/recommendation-history", methods=["GET"])
def recommendation_history():
    try:
        connection = sqlite3.connect(DATABASE_PATH)
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                id,
                farmer_name,
                location,
                recommended_crop,
                confidence,
                nitrogen,
                phosphorus,
                potassium,
                soil_ph,
                soil_moisture,
                rainfall,
                temperature,
                weather_rain_chance,
                created_at
            FROM recommendation_history
            ORDER BY id DESC
            LIMIT 10
        """)

        rows = cursor.fetchall()
        connection.close()

        history = [dict(row) for row in rows]

        return jsonify({
            "success": True,
            "history": history
        })

    except Exception as e:
        print("Recommendation history error:", e)

        return jsonify({
            "success": False,
            "error": str(e),
            "history": []
        }), 500

if __name__ == "__main__":

    print("")
    print("=" * 60)
    print("SMART CROP ADVISORY SYSTEM")
    print("=" * 60)

    print(
        "Crop ML Model:",
        "Loaded" if crop_model is not None else "NOT LOADED"
    )

    print(
        "Plant Disease AI:",
        "Loaded" if disease_model is not None else "NOT LOADED"
    )

    print(
        "Disease Classes:",
        len(disease_classes)
    )

    print("=" * 60)
    print("Server: http://127.0.0.1:5000")
    print("=" * 60)
    print("")

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )

@app.route("/api/recommendation-history", methods=["GET"])
def recommendation_history():
    try:
        connection = sqlite3.connect(DATABASE_PATH)
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()

        # Get the true total number of recommendations
        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM recommendation_history
        """)

        total = cursor.fetchone()["total"]

        # Get latest 10 recommendations
        cursor.execute("""
            SELECT
                id,
                farmer_name,
                location,
                recommended_crop,
                confidence,
                nitrogen,
                phosphorus,
                potassium,
                soil_ph,
                soil_moisture,
                rainfall,
                temperature,
                weather_rain_chance,
                created_at
            FROM recommendation_history
            ORDER BY id DESC
            LIMIT 10
        """)

        rows = cursor.fetchall()

        history = [dict(row) for row in rows]

        connection.close()

        return jsonify({
            "success": True,
            "total": total,
            "history": history
        })

    except Exception as e:

        print("Recommendation history error:", e)

        return jsonify({
            "success": False,
            "error": str(e),
            "total": 0,
            "history": []
        }), 500