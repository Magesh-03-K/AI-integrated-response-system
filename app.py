from flask import Flask, render_template, Response, request, jsonify
import cv2
import numpy as np
import tensorflow as tf
from playsound import playsound
import requests
import base64
from io import BytesIO
from PIL import Image

app = Flask(__name__)

# Load AI Model
model = tf.keras.models.load_model('first_aid_model.h5')

# Google Maps API Key (Replace with your actual API key)
API_KEY = "your-api-key-here"

def detect_emergency(frame):
    img = cv2.resize(frame, (224, 224))  # Resize to match model input
    img = np.expand_dims(img, axis=0) / 255.0  # Normalize
    prediction = model.predict(img)
    return np.argmax(prediction)

def play_audio_alert():
    playsound('alert.mp3')  # Play an emergency alert sound

def display_first_aid_instructions(emergency_type):
    instructions = {
        0: "No emergency detected.",
        1: "Fall detected! Ensure the person is responsive.",
        2: "Unconscious person detected! Call emergency services.",
        3: "Injury detected! Apply first aid immediately."
    }
    return instructions.get(emergency_type, "Unknown emergency.")

def find_nearby_emergency_services(latitude, longitude, service_type="hospital"):
    """ Finds nearby emergency services using Google Maps API """
    url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={latitude},{longitude}&radius=5000&type={service_type}&key={API_KEY}"
    response = requests.get(url)
    data = response.json()
    
    if "results" not in data:
        return []

    emergency_services = []
    for place in data["results"][:5]:  # Limit results to 5
        emergency_services.append({
            "name": place.get("name", "Unknown"),
            "address": place.get("vicinity", "No address available"),
            "latitude": place["geometry"]["location"]["lat"],
            "longitude": place["geometry"]["location"]["lng"]
        })
    
    return emergency_services

def generate_frames():
    cap = cv2.VideoCapture(0)  # Open webcam
    while True:
        success, frame = cap.read()
        if not success:
            break
        else:
            emergency_type = detect_emergency(frame)
            instructions = display_first_aid_instructions(emergency_type)

            if emergency_type != 0:
                play_audio_alert()

            # Draw text on the frame
            cv2.putText(frame, instructions, (50, 50), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            # Encode the frame
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()

            # Yield the frame
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/video_feed")
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route("/detect", methods=["GET"])
def detect():
    return render_template("detect.html")

@app.route("/emergency", methods=["GET"])
def emergency_page():
    latitude = request.args.get("latitude")
    longitude = request.args.get("longitude")
    service_type = request.args.get("type", "hospital")

    if not latitude or not longitude:
        return jsonify({"error": "Latitude and longitude are required"}), 400

    services = find_nearby_emergency_services(latitude, longitude, service_type)
    return render_template("emergency.html", services=services, service_type=service_type)

if __name__ == "__main__":
    app.run(debug=True)
