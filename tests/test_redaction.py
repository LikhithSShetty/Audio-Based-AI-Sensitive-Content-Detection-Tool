import unittest
from src.redaction.redact import Redactor

class TestRedactor(unittest.TestCase):

    def setUp(self):
        self.redactor = Redactor()
        self.original_video = "test_video.mp4"
        self.flagged_segments = [(10, 20), (30, 40)]

    def test_redact_video(self):
        redacted_video = self.redactor.redact_video(self.original_video, self.flagged_segments)
        self.assertIsNotNone(redacted_video)
        self.assertIn("redacted", redacted_video)  # Assuming the output filename contains 'redacted'

    def test_save_redacted_video(self):
        redacted_video = "redacted_test_video.mp4"
        result = self.redactor.save_redacted_video(redacted_video)
        self.assertTrue(result)  # Assuming the method returns True on success

if __name__ == '__main__':
    unittest.main()