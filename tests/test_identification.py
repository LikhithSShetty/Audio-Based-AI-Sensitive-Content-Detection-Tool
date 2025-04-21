import unittest
from src.identification.identify import Identifier

class TestIdentifier(unittest.TestCase):

    def setUp(self):
        self.identifier = Identifier()
        self.transcript = [
            {"text": "This is a confidential project.", "start": 0.0, "end": 5.0},
            {"text": "We are working on a prototype.", "start": 6.0, "end": 10.0},
            {"text": "This information is public.", "start": 11.0, "end": 15.0}
        ]
        self.criteria = {
            "keywords": ["confidential", "prototype"],
            "entity_types": ["ORGANIZATION", "PRODUCT"]
        }

    def test_identify_sensitive_content(self):
        flagged_segments = self.identifier.identify_sensitive_content(self.transcript, self.criteria)
        expected_segments = [(0.0, 5.0), (6.0, 10.0)]
        self.assertEqual(flagged_segments, expected_segments)

    def test_get_flagged_segments(self):
        self.identifier.identify_sensitive_content(self.transcript, self.criteria)
        flagged_segments = self.identifier.get_flagged_segments()
        expected_segments = [(0.0, 5.0), (6.0, 10.0)]
        self.assertEqual(flagged_segments, expected_segments)

if __name__ == '__main__':
    unittest.main()