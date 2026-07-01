"""Assemble Emotion_Detector_Submission.pdf from the project's real files and submission_assets/."""
import subprocess
from pathlib import Path

from fpdf import FPDF

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "submission_assets"

REPO_URL = "https://github.com/NonomiyaIzumi/emotion-detector-flask"

PENDING = "PENDING - see SKILLS_NETWORK_STEPS.md. Not yet provided."


ASCII_REPLACEMENTS = {
    "—": "-", "–": "-", "‘": "'", "’": "'",
    "“": '"', "”": '"', "…": "...",
}


def to_latin1(text):
    for unicode_char, ascii_char in ASCII_REPLACEMENTS.items():
        text = text.replace(unicode_char, ascii_char)
    return text.encode("latin-1", errors="replace").decode("latin-1")


def read_text_asset(name, mock_fallback=None):
    path = ASSETS / name
    if path.exists():
        return to_latin1(path.read_text(encoding="utf-8", errors="replace"))
    if mock_fallback:
        mock_path = ASSETS / mock_fallback
        if mock_path.exists():
            content = mock_path.read_text(encoding="utf-8", errors="replace")
            return to_latin1(
                "[SIMULATED - local mock Watson API, not the real Watson NLP service]\n\n" + content
            )
    return PENDING


def read_code(relative_path):
    return to_latin1((ROOT / relative_path).read_text(encoding="utf-8"))


def git_log_last_commit():
    try:
        return subprocess.run(
            ["git", "log", "-1", "--oneline"], cwd=ROOT, capture_output=True, text=True, check=True
        ).stdout.strip()
    except Exception:  # pylint: disable=broad-except
        return "unavailable"


class SubmissionPDF(FPDF):
    """PDF builder for the Emotion Detector final-project submission."""

    def task_header(self, title):
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(20, 20, 20)
        self.cell(0, 10, to_latin1(title), new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

    def sub_header(self, title):
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(60, 60, 60)
        self.cell(0, 8, to_latin1(title), new_x="LMARGIN", new_y="NEXT")

    def body_text(self, text):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(0, 0, 0)
        self.multi_cell(0, 5, to_latin1(text))
        self.ln(1)

    def code_block(self, code):
        self.set_font("Courier", "", 8)
        self.set_fill_color(245, 245, 245)
        self.set_text_color(0, 0, 0)
        self.multi_cell(0, 4, to_latin1(code), fill=True)
        self.ln(2)

    def output_block(self, text):
        is_pending = text == PENDING
        self.set_font("Courier", "" if not is_pending else "I", 9)
        if is_pending:
            self.set_text_color(180, 90, 0)
        else:
            self.set_fill_color(235, 245, 235)
            self.set_text_color(0, 60, 0)
        self.multi_cell(0, 5, to_latin1(text), fill=not is_pending)
        self.set_text_color(0, 0, 0)
        self.ln(2)

    def screenshot_or_placeholder(self, filename, caption):
        path = ASSETS / filename
        if path.exists():
            self.image(str(path), w=160)
            self.ln(2)
        else:
            self.set_font("Helvetica", "I", 10)
            self.set_text_color(180, 90, 0)
            self.multi_cell(0, 5, to_latin1(f"{PENDING} (expected file: submission_assets/{filename} - {caption})"))
            self.set_text_color(0, 0, 0)
            self.ln(2)


def build():
    pdf = SubmissionPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_margins(15, 15, 15)

    # Title page
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 20)
    pdf.cell(0, 15, "Emotion Detector - Final Project Submission", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 12)
    pdf.cell(0, 8, "Developing AI Applications with Python and Flask (IBM Skills Network)", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(0, 6, f"Repository: {REPO_URL}\nLast commit: {git_log_last_commit()}")
    pdf.ln(6)
    pdf.set_font("Helvetica", "I", 9)
    pdf.set_text_color(120, 120, 120)
    pdf.multi_cell(
        0, 5,
        "Sections marked \"Pending\" require the IBM Skills Network Cloud IDE (the Watson NLP "
        "endpoint used by this app only resolves inside that lab environment) and will be filled "
        "in once those outputs/screenshots are provided - see SKILLS_NETWORK_STEPS.md.",
    )
    pdf.set_text_color(0, 0, 0)

    # Task 1
    pdf.add_page()
    pdf.task_header("Task 1: Clone the project repository")
    pdf.sub_header("Public GitHub repository URL (contains README.md)")
    pdf.body_text(REPO_URL)
    pdf.sub_header("README.md")
    pdf.code_block(read_code("README.md"))

    # Task 2
    pdf.add_page()
    pdf.task_header("Task 2: Create an emotion detection application using the Watson NLP library")
    pdf.sub_header("Activity 1: EmotionDetection/emotion_detection.py")
    pdf.code_block(read_code("EmotionDetection/emotion_detection.py"))
    pdf.sub_header("Activity 2: terminal output - import and test without errors")
    pdf.output_block(read_text_asset("task2_raw_output.txt", mock_fallback="MOCK_task2_task3_output.txt"))

    # Task 3
    pdf.add_page()
    pdf.task_header("Task 3: Format the output of the application")
    pdf.sub_header("Activity 1: emotion_detector() returns the formatted dict (see code above)")
    pdf.body_text(
        "The emotion_detector function (Task 2 code above) already returns a dict with keys "
        "'anger', 'disgust', 'fear', 'joy', 'sadness', and 'dominant_emotion'."
    )
    pdf.sub_header("Activity 2: terminal output showing the accurate output format")
    pdf.output_block(read_text_asset("task3_formatted_output.txt", mock_fallback="MOCK_task2_task3_output.txt"))

    # Task 4
    pdf.add_page()
    pdf.task_header("Task 4: Package the application (validate the EmotionDetection package)")
    pdf.sub_header(f"Activity 1: {REPO_URL}/blob/master/EmotionDetection/__init__.py")
    pdf.code_block(read_code("EmotionDetection/__init__.py"))
    pdf.sub_header("Activity 2: terminal output validating EmotionDetection is a valid package")
    pdf.output_block(read_text_asset("task4_package_validation_output.txt"))

    # Task 5
    pdf.add_page()
    pdf.task_header("Task 5: Run unit tests on your application")
    pdf.sub_header("Activity 1: test_emotion_detection.py")
    pdf.code_block(read_code("test_emotion_detection.py"))
    pdf.sub_header("Activity 2: terminal output - all unit tests passed")
    pdf.output_block(read_text_asset("task5_unittest_output.txt", mock_fallback="MOCK_task5_unittest_output.txt"))

    # Task 6
    pdf.add_page()
    pdf.task_header("Task 6: Web deployment of the application using Flask")
    pdf.sub_header("Activity 1: server.py")
    pdf.code_block(read_code("server.py"))
    pdf.sub_header("Activity 2: screenshot 6b_deployment_test.png")
    pdf.screenshot_or_placeholder("6b_deployment_test.png", "browser screenshot of the deployed app with a result")

    # Task 7
    pdf.add_page()
    pdf.task_header("Task 7: Incorporate error handling")
    pdf.sub_header("Activity 1: emotion_detection.py - status code 400 handling (see Task 2 code above)")
    pdf.body_text(
        "emotion_detector() checks `response.status_code == 400` and returns a dict with all "
        "emotion scores and dominant_emotion set to None instead of raising an exception."
    )
    pdf.sub_header("Activity 2: server.py - handling of blank input errors (see Task 6 code above)")
    pdf.body_text(
        "In server.py, the /emotionDetector route checks `if response['dominant_emotion'] is "
        "None:` and returns (\"Invalid text! Please try again!\", 400)."
    )
    pdf.sub_header("Activity 3: screenshot 7c_error_handling_interface.png")
    pdf.screenshot_or_placeholder(
        "7c_error_handling_interface.png", "UI screenshot showing the blank-input error message"
    )

    # Task 8
    pdf.add_page()
    pdf.task_header("Task 8: Run static code analysis")
    pdf.sub_header("Activity 1: server.py (see Task 6 code above) analyzed with pylint")
    pdf.body_text("Command: uv run pylint server.py")
    pdf.sub_header("Activity 2: terminal output - perfect static-analysis score")
    pdf.output_block(read_text_asset("task8_pylint_output.txt"))

    out_path = ROOT / "Emotion_Detector_Submission.pdf"
    pdf.output(str(out_path))
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    build()
