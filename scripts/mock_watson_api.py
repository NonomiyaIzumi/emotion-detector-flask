"""Local stand-in for the Watson NLP EmotionPredict service, for local demo/preview only.

NOT part of the graded submission -- the real submission must call the real
sn-watson-emotion.labs.skillsnetwork.site endpoint from inside the IBM Skills
Network Cloud IDE. This mock exists so the app can be demoed on this machine.
"""
from flask import Flask, jsonify, request

app = Flask("Mock Watson NLP")

KEYWORDS = {
    "joy": ["happy", "glad", "joy", "delighted"],
    "anger": ["angry", "mad", "furious", "rage"],
    "disgust": ["disgust", "gross", "revolt"],
    "fear": ["afraid", "scared", "fear", "terrified"],
    "sadness": ["sad", "unhappy", "sorrow", "depressed"],
}

BASE_SCORE = 0.05


@app.route("/v1/watson.runtime.nlp.v1/NlpService/EmotionPredict", methods=["POST"])
def emotion_predict():
    payload = request.get_json(silent=True) or {}
    text = (payload.get("raw_document") or {}).get("text") or ""

    if not text.strip():
        return jsonify({"error": "no text provided"}), 400

    lowered = text.lower()
    scores = {emotion: BASE_SCORE for emotion in KEYWORDS}
    for emotion, words in KEYWORDS.items():
        if any(word in lowered for word in words):
            scores[emotion] = 0.85

    return jsonify({"emotionPredictions": [{"emotion": scores}]})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000)
