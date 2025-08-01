from flask import Flask, request, jsonify
from geopy.distance import geodesic
import random

app = Flask(__name__)

# Dummy DB of nearby doctors with GPS
doctor_db = [
    {"name": "Dr. Shuvo", "lat": 23.8123, "lon": 90.4135, "specialty": "General"},
    {"name": "Dr. Mim", "lat": 23.8115, "lon": 90.4172, "specialty": "Family Medicine"},
    {"name": "Dr. Zihan", "lat": 23.8097, "lon": 90.4102, "specialty": "Emergency"},
]

# AI-like symptom to alt-medicine recommendation
symptom_to_meds = {
    "fever": ["Paracetamol", "Ibuprofen", "Naproxen"],
    "headache": ["Aspirin", "Acetaminophen", "Naproxen"],
    "cough": ["Dextromethorphan", "Honey Syrup", "Expectorant"],
    "diarrhea": ["ORS", "Loperamide", "Probiotics"],
}

@app.route('/api/mapSearch', methods=['POST'])
def map_search():
    data = request.json
    symptom = data['symptom'].lower()
    user_loc = (data['location']['lat'], data['location']['lon'])

    medicines = symptom_to_meds.get(symptom, ["Consult a doctor"])

    # Find nearest doctors using geodesic distance
    def distance(doc):
        return geodesic(user_loc, (doc['lat'], doc['lon'])).km

    nearby_sorted = sorted(doctor_db, key=distance)
    for doc in nearby_sorted:
        doc['distance_km'] = round(distance(doc), 2)

    return jsonify({
        "symptom": symptom,
        "medicines": [{"name": med, "confidence": f"{random.randint(80,99)}%"} for med in medicines],
        "nearby_doctors": nearby_sorted[:3]
    })
