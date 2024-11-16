from flask import Flask, request, jsonify
import pickle
import numpy as np

app = Flask(__name__)

# Load models for each module
fertilizer_model = pickle.load(open('classifier.pkl', 'rb'))
fertilizer_info = pickle.load(open('fertilizer.pkl', 'rb'))
crop_model = pickle.load(open('model.pkl', 'rb'))
sc = pickle.load(open('standscaler.pkl', 'rb'))
ms = pickle.load(open('minmaxscaler.pkl', 'rb'))

# API for Fertilizer Recommendation
@app.route('/api/fertilizer/predict', methods=['POST'])
def api_fertilizer_predict():
    try:
        data = request.json
        required_fields = ['temp', 'humid', 'mois', 'soil', 'crop', 'nitro', 'pota', 'phos']

        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400

        input_data = [int(data[field]) for field in required_fields]

        # Predict the fertilizer class
        prediction_idx = fertilizer_model.predict([input_data])[0]

        # Retrieve the label using classes_
        result_label = fertilizer_info.classes_[prediction_idx] if hasattr(fertilizer_info, 'classes_') else 'Unknown'

        return jsonify({"fertilizer_recommendation": result_label}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# API for Crop Recommendation
@app.route('/api/crop/predict', methods=['POST'])
def api_crop_predict():
    try:
        data = request.json
        required_fields = ['Nitrogen', 'Phosphorus', 'Potassium', 'Temperature', 'Humidity', 'pH', 'Rainfall']

        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400

        # Collect data and convert it to appropriate types
        feature_list = [
            int(data['Nitrogen']),
            int(data['Phosphorus']),
            int(data['Potassium']),
            float(data['Temperature']),
            float(data['Humidity']),
            float(data['pH']),
            float(data['Rainfall'])
        ]
        single_pred = np.array(feature_list).reshape(1, -1)

        # Scaling and prediction
        scaled_features = ms.transform(single_pred)
        final_features = sc.transform(scaled_features)
        prediction = crop_model.predict(final_features)

        # Define crop mapping
        crop_dict = {
            1: "Rice", 2: "Maize", 3: "Jute", 4: "Cotton", 5: "Coconut", 6: "Papaya",
            7: "Orange", 8: "Apple", 9: "Muskmelon", 10: "Watermelon", 11: "Grapes",
            12: "Mango", 13: "Banana", 14: "Pomegranate", 15: "Lentil", 16: "Blackgram",
            17: "Mungbean", 18: "Mothbeans", 19: "Pigeonpeas", 20: "Kidneybeans",
            21: "Chickpea", 22: "Coffee"
        }

        result = crop_dict.get(prediction[0], 'Unknown crop')
        return jsonify({"crop_recommendation": result}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

import os

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))  # Get port from environment or default to 5000
    app.run(host='0.0.0.0', port=port)
