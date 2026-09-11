# Smart Crop Advisory System for Small and Marginal Farmers

## What is included
This is a runnable MVP for a college project. It includes:
- Farmer profile storage in SQLite
- Crop recommendation for the top 3 crops
- Soil/N-P-K/pH/rainfall/temperature inputs
- Demo weather profiles
- Irrigation advisory
- Nutrient advisory
- Weather alerts
- Disease-image workflow placeholder

## Run
1. Install Python 3.10+.
2. Open a terminal in this folder.
3. Create a virtual environment:
   `python -m venv .venv`
4. Activate it:
   - Windows: `.venv\Scripts\activate`
   - Linux/macOS: `source .venv/bin/activate`
5. Install dependencies:
   `pip install -r requirements.txt`
6. Start:
   `python app.py`
7. Open:
   `http://127.0.0.1:5000`

## Important
The current recommendation engine is a transparent demo scoring engine, not a validated agronomic model. For the competition/final version, replace the demo crop profiles with a verified agricultural dataset and add a properly trained ML model.

## Next development milestones
1. Replace demo scoring with Random Forest/XGBoost trained on a verified dataset.
2. Connect a real weather API.
3. Add soil-test/soil-card import.
4. Train a plant-disease image model using a verified dataset.
5. Add Kannada/Hindi translations and voice input.
6. Add notifications and an agriculture-officer/admin dashboard.
7. Conduct field/user testing with agriculture experts before making real-world recommendations.
