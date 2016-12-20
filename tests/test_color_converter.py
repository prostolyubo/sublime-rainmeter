"""Test color converter."""


import sys

from unittest import TestCase

COLOR_CONVERTER = sys.modules["Rainmeter.color.converter"]


class IntToHexTest(TestCase):
    """Testing int to hex conversion and its corner cases."""

    def test_below_lower_boundary(self):
        """Rainmeter only supports from 0 upwards."""
        self.assertRaises(AssertionError, COLOR_CONVERTER.int_to_hex, -1)

    def test_lower_boundary(self):
        """Zero is a corner case and should return 00."""
        hex_value = COLOR_CONVERTER.int_to_hex(0)

        self.assertEqual(hex_value, "00")

    def test_default(self):
        """A random number within the boundary 0, 255 should work."""
        hex_value = COLOR_CONVERTER.int_to_hex(128)

        self.assertEqual(hex_value, "80")

    def test_upper_boundary(self):
        """255 is a corner case and should return FF."""
        hex_value = COLOR_CONVERTER.int_to_hex(255)

        self.assertEqual(hex_value, "FF")

    def test_over_upper_boundary(self):
        """Rainmeter only supports up to 255."""
        self.assertRaises(AssertionError, COLOR_CONVERTER.int_to_hex, 256)

    def test_letter_case(self):
        """We also support lower case if it is requested."""
        hex_value = COLOR_CONVERTER.int_to_hex(255, letter_case=COLOR_CONVERTER.LetterCase.Lower)

        self.assertEqual(hex_value, "ff")


class RGBsToHexesTest(TestCase):
    """Testing RGBs to hexes conversion and its corner cases."""

    def test_default_rgb_conversion(self):
        """3 valid ints should convert to 3 hexes."""
        hexes = COLOR_CONVERTER.rgbs_to_hexes([128, 128, 128])

        self.assertEqual(hexes, ["80", "80", "80"])

    def test_default_rgba_conversion(self):
        """4 valid ints should convert to 4 hexes."""
        hexes = COLOR_CONVERTER.rgbs_to_hexes([128, 128, 128, 128])

        self.assertEqual(hexes, ["80", "80", "80", "80"])


    def test_invalid_rgb_low_len(self):
        """RGB are at least 3 values."""
        self.assertRaises(AssertionError, COLOR_CONVERTER.rgbs_to_hexes, [128, 128])

    def test_invalid_rgb_high_len(self):
        """RGB are at most 4 values."""
        self.assertRaises(AssertionError, COLOR_CONVERTER.rgbs_to_hexes, [128, 128, 128, 128, 128])


class HexesToStringTest(TestCase):
    """This test guerentees that a proper string conversion ."""

    def test_stringing(self):
        """Default case with one spacing."""
        stringed = COLOR_CONVERTER.hexes_to_string(["80", "80", "80"])

        self.assertEqual(stringed, "808080")

    def test_rgba(self):
        """RGBA case."""
        stringed = COLOR_CONVERTER.hexes_to_string(["80", "80", "80", "80"])

        self.assertEqual(stringed, "80808080")


class HexToIntTest(TestCase):
    """Testing hex to int conversion and its corner cases."""

    def test_below_lower_boundary(self):
        """Rainmeter only supports from 0 upwards."""
        self.assertRaises(AssertionError, COLOR_CONVERTER.hex_to_int, "-1")

    def test_lower_boundary(self):
        """00 is a corner case and should return 0."""
        int_value = COLOR_CONVERTER.hex_to_int("00")

        self.assertEqual(int_value, 0)

    def test_default(self):
        """A random number within the boundary 0, 255 should work."""
        int_value = COLOR_CONVERTER.hex_to_int("80")

        self.assertEqual(int_value, 128)

    def test_upper_boundary(self):
        """FF is a corner case and should return 255."""
        int_value = COLOR_CONVERTER.hex_to_int("FF")

        self.assertEqual(int_value, 255)

    def test_over_upper_boundary(self):
        """Rainmeter only supports up to 255."""
        self.assertRaises(AssertionError, COLOR_CONVERTER.hex_to_int, "100")


class HexesToRGBsTest(TestCase):
    """Testing Hexes to RGBs conversion and its corner cases."""

    def test_default_hex_conversion(self):
        """."""
        rgb = COLOR_CONVERTER.hexes_to_rgbs(["80", "80", "80"])

        self.assertEqual(rgb, [128, 128, 128])

    def test_default_hexa_conversion(self):
        """4 valid hexes should convert to rgba."""
        rgba = COLOR_CONVERTER.hexes_to_rgbs(["80", "80", "80", "80"])

        self.assertEqual(rgba, [128, 128, 128, 128])

    def test_invalid_hex_low_len(self):
        """Require at least 3 values."""
        self.assertRaises(AssertionError, COLOR_CONVERTER.hexes_to_rgbs, ["FF", "FF"])

    def test_invalid_hex_high_len(self):
        """Require at most 4 values."""
        self.assertRaises(
            AssertionError,
            COLOR_CONVERTER.hexes_to_rgbs,
            ["FF", "FF", "FF", "FF", "FF"]
        )


class RGBsToStringTest(TestCase):
    """This test guerentees that a proper string conversion ."""

    def test_stringing(self):
        """Default Rainmeter decimal color representation."""
        stringed = COLOR_CONVERTER.rgbs_to_string([128, 128, 128])

        self.assertEqual(stringed, "128,128,128")

    def test_with_spacing(self):
        """For people who like to space things."""
        stringed = COLOR_CONVERTER.rgbs_to_string([128, 128, 128], spacing=1)

        self.assertEqual(stringed, "128, 128, 128")

    def test_with_more_spacing(self):
        """For people who like to use a lot of spacings."""
        stringed = COLOR_CONVERTER.rgbs_to_string([128, 128, 128], spacing=5)

        self.assertEqual(stringed, "128,     128,     128")
