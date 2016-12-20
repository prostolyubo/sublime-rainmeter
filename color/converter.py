"""This module is about converting from/to Rainmeter RGB(A)."""

class LetterCase(object):
    """
    Represent how a hex value should be displayed.

    Depending on the incoming String
    we need to convert it to upper case or lower case.
    """
    Upper, Lower = range(1, 3)


def hex_to_int(hex_value):
    int_value = int(hex_value, 16)

    assert 0 <= int_value <= 255 

    return int_value

def hexes_to_rgbs(hexes):
    assert 3 <= len(hexes) <= 4

    return [hex_to_int(hex_value) for hex_value in hexes]

def hexes_to_string(hexes):
    """Convert hexes into a string representation."""

    return "".join(hexes)


def int_to_hex(int_value, letter_case=LetterCase.Upper):
    assert 0 <= int_value <= 255 

    # returns lower case hex values
    hex_value = hex(int_value)
    without_prefix = hex_value[2:]
    padded = without_prefix.zfill(2)

    if letter_case == LetterCase.Upper:
        padded = padded.upper()

    return padded

def rgbs_to_hexes(rgbs):
    assert 3 <= len(rgbs) <= 4

    return [int_to_hex(rgb) for rgb in rgbs]

def rgbs_to_string(rgbs, spacing=0):
    """Convert RGBs into a string representation."""
    joiner = ",".ljust(spacing + 1)

    # you cant join ints
    return joiner.join(str(x) for x in rgbs)
