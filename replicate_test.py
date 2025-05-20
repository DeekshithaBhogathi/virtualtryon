from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import time

app = Flask(__name__)
CORS(app)

REPLICATE_API_TOKEN = "r8_fK2c5D2OHEIMCVYwB3bAWOMyij9wAbh18opUF"

@app.route('/api/generate-cloth', methods=['POST'])
def generate_cloth():
    data = request.get_json()
    prompt = data.get("prompt", "")

    try:
        prediction_res = requests.post(
            "https://api.replicate.com/v1/predictions",
            headers={
                "Authorization": f"Token {REPLICATE_API_TOKEN}",
                "Content-Type": "application/json"
            },
            json={
                "version": "db21e45f8fd4c16a295f86c9275f5a53b548b8e83ad1c09400a871d75edc0616",
                "input": {
                    "prompt": prompt,
                    "width": 768,
                    "height": 768,
                    "num_outputs": 1
                }
            }
        )

        prediction = prediction_res.json()
        prediction_id = prediction.get("id")

        for _ in range(60):
            time.sleep(3)
            status_res = requests.get(
                f"https://api.replicate.com/v1/predictions/{prediction_id}",
                headers={"Authorization": f"Token {REPLICATE_API_TOKEN}"}
            )
            result = status_res.json()
            if result["status"] == "succeeded":
                return jsonify({ "image_url": result["output"][0] })
            elif result["status"] == "failed":
                return jsonify({ "error": "Image generation failed." }), 500
            print(f"⏳ Status: {result['status']}")

        return jsonify({ "error": "Image generation timed out." }), 504

    except Exception as e:
        print("❌ Replicate generation error:", e)
        return jsonify({ "error": str(e) }), 500

@app.route('/')
def home():
    return "✅ Replicate SDXL backend is running."

if __name__ == '__main__':
    app.run(debug=True, port=5050)
