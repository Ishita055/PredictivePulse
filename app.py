from flask import Flask, request, jsonify, render_template
import pickle
import numpy as np

app = Flask(__name__)

# Load Model and Scaler at startup
model = None
scaler = None

try:
    with open('logreg_model.pkl', 'rb') as f:
        model = pickle.load(f)
    print("Model loaded successfully.")
except FileNotFoundError:
    print("Error: logreg_model.pkl not found. Please run train_model.py first.")

try:
    with open('scaler.pkl', 'rb') as f:
        scaler = pickle.load(f)
    print("Scaler loaded successfully.")
except FileNotFoundError:
    print("Error: scaler.pkl not found. Please run train_model.py first.")


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    if model is None or scaler is None:
        return jsonify({'error': 'Model or scaler not initialized'}), 500
        
    try:
        data = request.json
        print("Received data:", data)
        
        # Mappings matching the training data logic
        gender_map = {'Male': 0, 'Female': 1}
        binary_map = {'No': 0, 'Yes': 1}
        age_map = {'18-34 years': 1, '35-50 years': 2, '51-64 years': 3, '65+ years': 4}
        severity_map = {'Mild': 0, 'Moderate': 1, 'Severe': 2}
        when_map = {'Less than 1 Year': 1, '1 - 5 Years': 2, 'More than 5 Years': 3}
        
        # Mapping inputs directly from the frontend strings
        # E.g '100-110 mmHg (Normal)' -> need to map to ordinal categories
        # Let's map based on the category we trained on (1, 2, 3)
        def map_systolic(s_val):
            # Simplistic parsing based on frontend values mapping back to training ordinals
            if '100-110' in s_val or 'Normal' in s_val:
                return 0
            elif '111 - 120' in s_val:
                return 1
            elif '121-130' in s_val or 'Stage 1' in s_val:
                return 2
            elif '130+' in s_val or 'Stage 2' in s_val or 'Crisis' in s_val:
                return 3
            return 1 # default
            
        def map_diastolic(d_val):
            if '70 - 80' in d_val or 'Normal' in d_val:
                return 0
            elif '81 - 90' in d_val:
                return 1
            elif '91-100' in d_val or 'Stage 1' in d_val:
                return 2
            elif '100+' in d_val or 'Stage 2' in d_val or 'Crisis' in d_val:
                return 3
            return 1 # default

        # Extract and encode features in the EXACT order as training data
        # 'Age', 'History', 'Patient', 'TakeMedication', 'Severity',
        # 'BreathShortness', 'VisualChanges', 'NoseBleeding', 'Whendiagnoused',
        # 'Systolic', 'Diastolic', 'ControlledDiet', 'Gender'
        
        # Re-ordering to match the X columns from training:
        # ['Gender', 'Age', 'History', 'Patient', 'TakeMedication', 'Severity',
        #  'BreathShortness', 'VisualChanges', 'NoseBleeding', 'Whendiagnoused',
        #  'Systolic', 'Diastolic', 'ControlledDiet']
        
        features = [
            gender_map.get(data.get('Gender', 'Male'), 0),
            age_map.get(data.get('AgeGroup', '18-34 years'), 1),
            binary_map.get(data.get('FamilyHistory', 'No'), 0),
            binary_map.get(data.get('UnderMedicalCare', 'No'), 0), # Maps to 'Patient'
            binary_map.get(data.get('TakingBPMedication', 'No'), 0),
            severity_map.get(data.get('SymptomSeverity', 'Mild'), 0),
            binary_map.get(data.get('ShortnessOfBreath', 'No'), 0),
            binary_map.get(data.get('VisionChanges', 'No'), 0),
            binary_map.get(data.get('FrequentNosebleeds', 'No'), 0),
            when_map.get(data.get('TimeSinceDiagnosis', 'Less than 1 Year'), 1),
            map_systolic(data.get('SystolicPressure', '')),
            map_diastolic(data.get('DiastolicPressure', '')),
            binary_map.get(data.get('HeartHealthyDiet', 'No'), 0) # Maps to 'ControlledDiet'
        ]
        
        # Convert to numpy array and reshape
        features_array = np.array(features).reshape(1, -1)
        
        # Scale features
        scaled_features = scaler.transform(features_array)
        
        # Predict
        prediction = model.predict(scaled_features)[0]
        # Get probability/confidence
        probabilities = model.predict_proba(scaled_features)[0]
        confidence = float(max(probabilities) * 100)
        
        # Result mapping
        # 0: Normal, 1: Stage-1, 2: Stage-2, 3: Crisis
        # Note: Depending on data, 0 might not exist or might be mapped slightly differently,
        # but the frontend gracefully handles the return values.
        result_map = {
            0: 'NORMAL',
            1: 'STAGE_1',
            2: 'STAGE_2',
            3: 'CRISIS'
        }
        
        predicted_stage = result_map.get(int(prediction), 'NORMAL')

        return jsonify({
            'success': True,
            'prediction': predicted_stage,
            'confidence': f"{confidence:.1f}%"
        })

    except Exception as e:
        print(f"Prediction Error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5000)
