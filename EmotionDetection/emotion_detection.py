"""Emotion detection module using the Watson NLP EmotionPredict service."""

import json
import os
import requests

DEFAULT_WATSON_NLP_URL = (
    "https://sn-watson-emotion.labs.skills.network/"
    "v1/watson.runtime.nlp.v1/NlpService/EmotionPredict"
)
DEFAULT_MODEL_ID = "emotion_aggregated-workflow_lang_en_stock"
EMOTION_KEYS = ("anger", "disgust", "fear", "joy", "sadness")


def _empty_emotion_result():
    """Return an emotion result dictionary with None values for error cases."""
    result = {key: None for key in EMOTION_KEYS}
    result["dominant_emotion"] = None
    return result


def emotion_detector(text_to_analyze):
    """Analyze the emotion of the given text using the Watson NLP service.

    Args:
        text_to_analyze (str): The input text to analyze.

    Returns:
        dict: A dictionary containing scores for anger, disgust, fear, joy,
            sadness, and the dominant_emotion label (or None values on error).
    """
    url = os.environ.get("WATSON_NLP_URL", DEFAULT_WATSON_NLP_URL)
    headers = {
        "grpc-metadata-mm-model-id": os.environ.get(
            "WATSON_NLP_MODEL_ID", DEFAULT_MODEL_ID
        )
    }
    myobj = {"raw_document": {"text": text_to_analyze}}

    try:
        response = requests.post(
            url,
            json=myobj,
            headers=headers,
            timeout=10,
        )
    except requests.exceptions.RequestException:
        return _empty_emotion_result()

    if response.status_code == 400:
        return _empty_emotion_result()

    if response.status_code != 200:
        return _empty_emotion_result()

    try:
        formatted_response = json.loads(response.text)
        emotions = formatted_response["emotionPredictions"][0]["emotion"]
        emotion_scores = {key: emotions[key] for key in EMOTION_KEYS}
    except (ValueError, KeyError, IndexError, TypeError):
        return _empty_emotion_result()

    dominant_emotion = max(emotion_scores, key=emotion_scores.get)

    return {
        "anger": emotion_scores["anger"],
        "disgust": emotion_scores["disgust"],
        "fear": emotion_scores["fear"],
        "joy": emotion_scores["joy"],
        "sadness": emotion_scores["sadness"],
        "dominant_emotion": dominant_emotion,
    }
