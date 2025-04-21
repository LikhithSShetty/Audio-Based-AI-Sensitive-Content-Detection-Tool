import unittest
from src.transcription.transcribe import Transcriber

class TestTranscriber(unittest.TestCase):

    def setUp(self):
        self.transcriber = Transcriber()

    def test_transcribe_video(self):
        video_file = "path/to/test_video.mp4"
        result = self.transcriber.transcribe_video(video_file)
        self.assertIsNotNone(result)
        self.assertIn("Welcome everyone", result)

    def test_get_transcript(self):
        self.transcriber.transcribe_video("path/to/test_video.mp4")
        transcript = self.transcriber.get_transcript()
        self.assertIsInstance(transcript, str)
        self.assertGreater(len(transcript), 0)

if __name__ == '__main__':
    unittest.main()