"""Run the Emotion Detector app against the local mock Watson API for a local preview.

NOT for submission -- these outputs are simulated, not from the real Watson NLP
service. Use SKILLS_NETWORK_STEPS.md to produce the genuine outputs required
for grading. This script only redirects network calls; EmotionDetection/ and
server.py are untouched.
"""
import sys
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "submission_assets"
sys.path.insert(0, str(ROOT))

REAL_URL_PREFIX = "https://sn-watson-emotion.labs.skillsnetwork.site"
MOCK_URL_PREFIX = "http://127.0.0.1:8000"

_original_post = requests.post


def _patched_post(url, *args, **kwargs):
    if url.startswith(REAL_URL_PREFIX):
        url = MOCK_URL_PREFIX + url[len(REAL_URL_PREFIX):]
    return _original_post(url, *args, **kwargs)


requests.post = _patched_post

from EmotionDetection.emotion_detection import emotion_detector  # noqa: E402


def main():
    ASSETS.mkdir(exist_ok=True)

    lines = []
    lines.append(">>> from EmotionDetection.emotion_detection import emotion_detector")
    lines.append(">>> emotion_detector(\"I am so happy I am doing this\")")
    result = emotion_detector("I am so happy I am doing this")
    lines.append(repr(result))
    (ASSETS / "MOCK_task2_task3_output.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("\n".join(lines))

    test_cases = {
        "I am so happy I am doing this": "joy",
        "I am so angry I could scream": "anger",
        "I am so disgusted by this": "disgust",
        "I am so scared and afraid": "fear",
        "I am so sad about this": "sadness",
    }
    test_lines = ["test_emotion_detection (test_emotion_detection.TestEmotionDetection) ... ", ""]
    all_pass = True
    for text, expected in test_cases.items():
        got = emotion_detector(text)["dominant_emotion"]
        ok = got == expected
        all_pass = all_pass and ok
        test_lines.append(f"  {text!r} -> {got} (expected {expected}) {'OK' if ok else 'FAIL'}")

    test_lines.append("")
    test_lines.append("OK" if all_pass else "FAILED")
    test_lines.append("Ran 1 test in 0.05s")
    (ASSETS / "MOCK_task5_unittest_output.txt").write_text("\n".join(test_lines) + "\n", encoding="utf-8")
    print("\n".join(test_lines))

    blank_result = emotion_detector("")
    print("Blank input result:", blank_result)


if __name__ == "__main__":
    main()
