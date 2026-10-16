import unittest
from sentinel.zone import point_in_polygon, foot_point, DwellTracker

SQ = [[0, 0], [10, 0], [10, 10], [0, 10]]

class T(unittest.TestCase):
    def test_pip(self):
        self.assertTrue(point_in_polygon(5, 5, SQ)); self.assertFalse(point_in_polygon(15, 5, SQ))
    def test_foot(self):
        self.assertEqual(foot_point((2, 3, 4, 6)), (4.0, 9))
    def test_dwell_fires_once_then_cooldown(self):
        t = DwellTracker(SQ, "z", dwell_s=2, cooldown_s=10); b = (4, 0, 2, 6)
        self.assertIsNone(t.update(1, b, 0)); self.assertIsNone(t.update(1, b, 1.9))
        self.assertAlmostEqual(t.update(1, b, 2.1), 2.1)
        self.assertIsNone(t.update(1, b, 5)); self.assertIsNotNone(t.update(1, b, 12.2))
    def test_leaving_resets(self):
        t = DwellTracker(SQ, "z", dwell_s=2); t.update(1, (4, 0, 2, 6), 0); t.update(1, (40, 0, 2, 6), 1)
        self.assertIsNone(t.update(1, (4, 0, 2, 6), 2.5))
    def test_tracks_independent(self):
        t = DwellTracker(SQ, "z", dwell_s=1); t.update(1, (4, 0, 2, 6), 0)
        self.assertIsNone(t.update(2, (4, 0, 2, 6), 1)); self.assertIsNotNone(t.update(1, (4, 0, 2, 6), 1))

if __name__ == "__main__": unittest.main()
