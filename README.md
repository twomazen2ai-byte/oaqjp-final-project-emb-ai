# Final Project

## Project Overview

**Emotion Detector** is an AI-powered Python and Flask web application developed for the IBM Skills Network final project (*Developing AI Applications with Python and Flask*). The application analyzes user-provided text using the **Watson NLP Emotion Predict** service (`emotion_aggregated-workflow_lang_en_stock`), extracts scores across five core emotion dimensions (`anger`, `disgust`, `fear`, `joy`, and `sadness`), identifies the `dominant_emotion`, and presents a formatted analysis through an interactive web interface.

---

## Repository Structure

```text
.
├── EmotionDetection/
│   ├── __init__.py              # Package initializer exporting emotion_detection
│   └── emotion_detection.py     # Core Watson NLP emotion_detector() implementation
├── emotion_detection.py         # Root-level module re-exporting emotion_detector()
├── server.py                    # Flask web server exposing / and /emotionDetector
├── test_emotion_detection.py    # Unit tests covering all 5 emotions, schema, and errors
├── templates/
│   └── index.html               # Bootstrap-based web UI template
├── static/
│   └── mywebscript.js           # Frontend XHR handler for /emotionDetector
├── requirements.txt             # Python dependencies (Flask, requests, pylint)
├── evidence/                    # Verified terminal outputs and submission artifacts
└── README.md                    # Project documentation
```

---

## Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone https://github.com/twomazen2ai-byte/flaskprog.git
   cd flaskprog
   ```

2. **Create and activate a virtual environment (optional but recommended):**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration (Optional):**
   By default, the application uses the IBM Skills Network Watson NLP endpoint:
   - `WATSON_NLP_URL`: `https://sn-watson-emotion.labs.skills.network/v1/watson.runtime.nlp.v1/NlpService/EmotionPredict`
   - `WATSON_NLP_MODEL_ID`: `emotion_aggregated-workflow_lang_en_stock`

---

## Execution Commands

### 1. Run Interactive Package Validation
```bash
python3 -c "from EmotionDetection.emotion_detection import emotion_detector; print(emotion_detector('I hate working long hours'))"
```

### 2. Start the Flask Web Application
```bash
python3 server.py
```
The server starts on `http://0.0.0.0:5000`. Open `http://localhost:5000` in your browser, enter a statement to analyze, and click **Run Sentiment Analysis**.

---

## Testing & Static Code Analysis Instructions

### 1. Run Unit Tests
```bash
python3 -m unittest -v test_emotion_detection.py
```

### 2. Run Static Code Analysis (PyLint)
```bash
python3 -m pylint server.py EmotionDetection/emotion_detection.py EmotionDetection/__init__.py emotion_detection.py test_emotion_detection.py
```
