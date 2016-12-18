"""This module provides distance calculations using the levenshtein metric."""


def levenshtein(top_string, bot_string):
    """
    The Levenshtein distance is a string metric for measuring the difference between two sequences.

    Informally,
    the Levenshtein distance between two words is the minimum number of single-character edits
    (i.e. insertions, deletions or substitutions) required to change one word into the other.
    """
    if len(top_string) < len(bot_string):
        return levenshtein(bot_string, top_string)

    # len(s1) >= len(s2)
    if len(bot_string) == 0:
        return len(top_string)

    previous_row = range(len(bot_string) + 1)
    for i, top_char in enumerate(top_string):
        current_row = [i + 1]
        for j, bot_char in enumerate(bot_string):
            # j+1 instead of j since previous_row and current_row are one character longer
            # than bot_string
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (top_char != bot_char)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]
