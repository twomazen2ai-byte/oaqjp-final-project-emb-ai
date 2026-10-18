"""Emotion detection module using the Watson NLP EmotionPredict service."""

from EmotionDetection.emotion_detection import (
    DEFAULT_MODEL_ID,
    DEFAULT_WATSON_NLP_URL,
    emotion_detector,
)

__all__ = [
    "DEFAULT_MODEL_ID",
    "DEFAULT_WATSON_NLP_URL",
    "emotion_detector",
]
