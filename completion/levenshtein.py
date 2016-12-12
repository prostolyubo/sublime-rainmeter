def levenshtein(top_string, bot_string):
    if len(top_string) < len(bot_string):
        return levenshtein(bot_string, top_string)

    # len(s1) >= len(s2)
    if len(bot_string) == 0:
        return len(top_string)

    previous_row = range(len(bot_string) + 1)
    for i, top_char in enumerate(top_string):
        current_row = [i + 1]
        for j, bot_char in enumerate(bot_string):
            insertions = previous_row[j + 1] + 1  # j+1 instead of j since previous_row and current_row are one character longer
            deletions = current_row[j] + 1        # than bot_string
            substitutions = previous_row[j] + (top_char != bot_char)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]
