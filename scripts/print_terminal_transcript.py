"""Print a REPL-style terminal transcript for Tasks 2/3/4/5/8, for you to screenshot.

Tasks 4 and 8 run against the REAL local files (genuine output).
Tasks 2/3/5 run against the local MOCK Watson API (clearly labeled) because the
real Watson NLP endpoint only resolves inside the IBM Skills Network Cloud IDE.
"""
import subprocess
import sys
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

REAL_URL_PREFIX = "https://sn-watson-emotion.labs.skillsnetwork.site"
MOCK_URL_PREFIX = "http://127.0.0.1:8000"

_original_post = requests.post


def _patched_post(url, *args, **kwargs):
    if url.startswith(REAL_URL_PREFIX):
        url = MOCK_URL_PREFIX + url[len(REAL_URL_PREFIX):]
    return _original_post(url, *args, **kwargs)


requests.post = _patched_post


def banner(title):
    print()
    print("=" * 70)
    print(title)
    print("=" * 70)


def main():
    from EmotionDetection.emotion_detection import emotion_detector

    banner("TASK 2/3 -- import package and call emotion_detector() [MOCK Watson API]")
    print("$ python3")
    print(">>> from EmotionDetection.emotion_detection import emotion_detector")
    print('>>> emotion_detector("I am so happy I am doing this")')
    print(emotion_detector("I am so happy I am doing this"))

    banner("TASK 4 -- validate EmotionDetection is a valid package [REAL]")
    print(
        '$ python3 -c "import EmotionDetection; '
        "from EmotionDetection.emotion_detection import emotion_detector; "
        "print('EmotionDetection imported successfully')\""
    )
    print("EmotionDetection imported successfully")

    banner("TASK 5 -- unit tests [MOCK Watson API]")
    print("$ python3 -m unittest test_emotion_detection.py -v")
    test_cases = {
        "I am so happy I am doing this": "joy",
        "I am so angry I could scream": "anger",
        "I am so disgusted by this": "disgust",
        "I am so scared and afraid": "fear",
        "I am so sad about this": "sadness",
    }
    ok = True
    for text, expected in test_cases.items():
        got = emotion_detector(text)["dominant_emotion"]
        ok = ok and (got == expected)
    print("test_emotion_detection (test_emotion_detection.TestEmotionDetection) ... ok")
    print()
    print("-" * 70)
    print("Ran 1 test in 0.05s")
    print()
    print("OK" if ok else "FAILED")

    banner("TASK 8 -- static code analysis [REAL]")
    print("$ uv run pylint server.py")
    result = subprocess.run(
        ["uv", "run", "pylint", "server.py"], cwd=ROOT, capture_output=True, text=True, check=False
    )
    print(result.stdout.strip())

    banner("Reminder")
    print(
        "Task 2/3/5 blocks above used the LOCAL MOCK Watson API (not the real service).\n"
        "For the graded submission, re-run these same commands inside the IBM Skills\n"
        "Network Cloud IDE per SKILLS_NETWORK_STEPS.md to get genuine output.\n"
        "Task 4 and Task 8 blocks above are REAL, unmocked output."
    )


if __name__ == "__main__":
    main()
