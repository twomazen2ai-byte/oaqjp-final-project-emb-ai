"""Unit tests for the EmotionDetection package and Flask server."""

import json
import unittest
from unittest.mock import MagicMock, patch
import requests
from EmotionDetection.emotion_detection import (
    DEFAULT_MODEL_ID,
    DEFAULT_WATSON_NLP_URL,
    emotion_detector,
)
from server import app


MOCK_EMOTION_RESPONSES = {
    "I am glad this happened": {
        "anger": 0.0043188,
        "disgust": 0.0012594,
        "fear": 0.0034721,
        "joy": 0.9854123,
        "sadness": 0.0089124,
    },
    "I am really mad about this": {
        "anger": 0.9412831,
        "disgust": 0.0213491,
        "fear": 0.0154829,
        "joy": 0.0021482,
        "sadness": 0.0197367,
    },
    "I feel disgusted just hearing about this": {
        "anger": 0.0312841,
        "disgust": 0.9384712,
        "fear": 0.0098412,
        "joy": 0.0012841,
        "sadness": 0.0191194,
    },
    "I am so sad about this": {
        "anger": 0.0084123,
        "disgust": 0.0041289,
        "fear": 0.0142891,
        "joy": 0.0021849,
        "sadness": 0.9709848,
    },
    "I am really afraid that this will happen": {
        "anger": 0.0061284,
        "disgust": 0.0031842,
        "fear": 0.9684129,
        "joy": 0.0018421,
        "sadness": 0.0204324,
    },
    "I love this new technology.": {
        "anger": 0.01364663,
        "disgust": 0.0017160787,
        "fear": 0.008986978,
        "joy": 0.9719017,
        "sadness": 0.055187024,
    },
}


def _build_watson_response(status_code=200, emotions=None, raw_text=None):
    """Build a mock requests.Response object matching Watson NLP format."""
    mock_response = MagicMock()
    mock_response.status_code = status_code
    if raw_text is not None:
        mock_response.text = raw_text
    elif emotions is not None:
        mock_response.text = json.dumps(
            {"emotionPredictions": [{"emotion": emotions}]}
        )
    else:
        mock_response.text = ""
    return mock_response


def _mock_post_side_effect(*_args, **kwargs):
    """Return deterministic Watson NLP mock responses based on input text."""
    payload = kwargs.get("json") or {}
    text = payload.get("raw_document", {}).get("text", "")
    if not text or not text.strip():
        return _build_watson_response(status_code=400)
    emotions = MOCK_EMOTION_RESPONSES.get(text)
    if emotions is None:
        return _build_watson_response(status_code=400)
    return _build_watson_response(status_code=200, emotions=emotions)


class TestEmotionDetector(unittest.TestCase):
    """Test suite for emotion_detector and Flask routes."""

    @patch(
        "EmotionDetection.emotion_detection.requests.post",
        side_effect=_mock_post_side_effect,
    )
    def test_emotion_detector(self, mock_post):
        """Verify the five required course statements and dominant emotions."""
        result_1 = emotion_detector("I am glad this happened")
        self.assertEqual(result_1["dominant_emotion"], "joy")

        result_2 = emotion_detector("I am really mad about this")
        self.assertEqual(result_2["dominant_emotion"], "anger")

        result_3 = emotion_detector("I feel disgusted just hearing about this")
        self.assertEqual(result_3["dominant_emotion"], "disgust")

        result_4 = emotion_detector("I am so sad about this")
        self.assertEqual(result_4["dominant_emotion"], "sadness")

        result_5 = emotion_detector("I am really afraid that this will happen")
        self.assertEqual(result_5["dominant_emotion"], "fear")

        self.assertEqual(mock_post.call_count, 5)

    @patch(
        "EmotionDetection.emotion_detection.requests.post",
        side_effect=_mock_post_side_effect,
    )
    def test_output_format_and_request_contract(self, mock_post):
        """Verify output schema, numeric values, and Watson request contract."""
        text = "I love this new technology."
        result = emotion_detector(text)

        expected_keys = {
            "anger",
            "disgust",
            "fear",
            "joy",
            "sadness",
            "dominant_emotion",
        }
        self.assertEqual(set(result.keys()), expected_keys)
        for key in ("anger", "disgust", "fear", "joy", "sadness"):
            self.assertIsInstance(result[key], float)
            self.assertAlmostEqual(
                result[key], MOCK_EMOTION_RESPONSES[text][key]
            )
        self.assertEqual(result["dominant_emotion"], "joy")

        mock_post.assert_called_once_with(
            DEFAULT_WATSON_NLP_URL,
            json={"raw_document": {"text": text}},
            headers={"grpc-metadata-mm-model-id": DEFAULT_MODEL_ID},
            timeout=10,
        )

    @patch("EmotionDetection.emotion_detection.requests.post")
    def test_http_400_returns_none_values(self, mock_post):
        """Verify HTTP 400 returns a dictionary with None for all fields."""
        mock_post.return_value = _build_watson_response(status_code=400)
        result = emotion_detector("")
        expected = {
            "anger": None,
            "disgust": None,
            "fear": None,
            "joy": None,
            "sadness": None,
            "dominant_emotion": None,
        }
        self.assertEqual(result, expected)

    @patch("EmotionDetection.emotion_detection.requests.post")
    def test_malformed_json_returns_none_values(self, mock_post):
        """Verify malformed JSON response is handled safely."""
        mock_post.return_value = _build_watson_response(
            status_code=200, raw_text="not-valid-json"
        )
        result = emotion_detector("Some text")
        self.assertIsNone(result["dominant_emotion"])
        self.assertTrue(all(value is None for value in result.values()))

    @patch("EmotionDetection.emotion_detection.requests.post")
    def test_request_exception_returns_none_values(self, mock_post):
        """Verify network errors return None values without raising."""
        mock_post.side_effect = requests.exceptions.ConnectTimeout("timeout")
        result = emotion_detector("I am glad this happened")
        self.assertIsNone(result["dominant_emotion"])
        self.assertTrue(all(value is None for value in result.values()))

    def test_flask_server_routes_and_error_handling(self):
        """Verify Flask index route, valid detection, and blank input handling."""
        client = app.test_client()

        index_resp = client.get("/")
        self.assertEqual(index_resp.status_code, 200)
        self.assertIn(b"NLP - Emotion Detection", index_resp.data)

        with patch(
            "EmotionDetection.emotion_detection.requests.post",
            side_effect=_mock_post_side_effect,
        ) as mock_post:
            blank_resp = client.get("/emotionDetector?textToAnalyze=")
            self.assertEqual(blank_resp.status_code, 200)
            self.assertEqual(
                blank_resp.get_data(as_text=True),
                "Invalid text! Please try again!",
            )

            ws_resp = client.get("/emotionDetector?textToAnalyze=%20%20%20")
            self.assertEqual(ws_resp.status_code, 200)
            self.assertEqual(
                ws_resp.get_data(as_text=True),
                "Invalid text! Please try again!",
            )
            self.assertEqual(mock_post.call_count, 0)

            valid_resp = client.get(
                "/emotionDetector?textToAnalyze=I%20love%20this%20new%20technology."
            )
            self.assertEqual(valid_resp.status_code, 200)
            self.assertEqual(
                valid_resp.get_data(as_text=True),
                "For the given statement, the system response is "
                "'anger': 0.01364663, 'disgust': 0.0017160787, "
                "'fear': 0.008986978, 'joy': 0.9719017 and "
                "'sadness': 0.055187024. The dominant emotion is joy.",
            )


if __name__ == "__main__":
    unittest.main()
