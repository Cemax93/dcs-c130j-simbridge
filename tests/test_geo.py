import unittest

from dcs_c130j_simbridge.geo import (
    calculate_distance_nm,
    dec_to_c130_coord,
    generate_approach_fix,
    parse_coordinate,
    runway_vector,
)


class CoordinateTests(unittest.TestCase):
    def test_decimal_coordinate_is_unchanged(self):
        self.assertEqual(parse_coordinate("45.5"), 45.5)

    def test_cardinal_coordinate_is_converted(self):
        self.assertAlmostEqual(parse_coordinate("S 45 30"), -45.5)
        self.assertAlmostEqual(parse_coordinate("037 30 E"), 37.5)

    def test_c130_format_uses_expected_precision(self):
        self.assertEqual(dec_to_c130_coord(45.5, -37.5), "N45^30.00 W037^30.00")

    def test_distance_between_same_point_is_zero(self):
        self.assertAlmostEqual(calculate_distance_nm(45, 37, 45, 37), 0)

    def test_approach_fix_requires_a_runway_number(self):
        self.assertIsNone(generate_approach_fix(45, 37, "unknown"))

    def test_runway_vector_starts_at_airport(self):
        vector = runway_vector(45, 37, "09", length_nm=5)
        self.assertIsNotNone(vector)
        self.assertEqual(vector[0], (45, 37))
        self.assertGreater(vector[1][1], 37)
