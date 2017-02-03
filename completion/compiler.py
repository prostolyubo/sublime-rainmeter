"""Compiler help reduce the complexity of the YAML files."""

from ..logger import error


def compile_keys(options):
    """
    Completion can contain lots of duplicate information.

    For example the trigger is most of the time also the result.
    Only in case of a value attribute is that returned.
    It also takes hints into consideration for compilation.
    """
    compiled_keys = []
    for option in options:
        key = option['title']
        display = option['title'] + "\t" + option['hint']

        if 'value' in option:
            result = option['value']
        else:
            result = option['title']
        if 'unique' in option:
            unique = option['unique']
        else:
            unique = False

        compiled_key = (key, display, result, unique)
        compiled_keys.append(compiled_key)

    return compiled_keys


def compile_values(options):
    """
    Bake completions from the provided YAML options.

    Considers stuff like hints and values.
    """
    key_to_values = dict()
    for option in options:
        option_key = option['title']
        compiled_values = list()
        if 'values' in option:
            option_values = option['values']

            for option_value in option_values:
                compiled_value = __compile_value(option_value)
                compiled_values.append(compiled_value)

        key_to_values[option_key] = compiled_values

    return key_to_values


def __compile_value(value_elements):
    """
    Transpile a list of elements into a sublime text completion scheme.

    A completion scheme is a tuple constructed as:

        (key\thint, value)

    key is display on the left side of the completion.
    hint is displayed on the right side of the completion and optional.
    It has to be seperated from the key using the escaped tabulator \t.
    value is the actual rendered content if the key trigger is activated.
    ."""
    length = len(value_elements)

    # case 1 is if only the key is provided, is generally the default case.
    # Meaning is generally explained in the key
    if length == 1:
        return value_elements[0] + "\tDefault", value_elements[0]

    # case 2 is if only the key and the special hint is given
    # means that the key is the value too
    elif length == 2:
        open_value_key, option_value_hint = value_elements
        return open_value_key + "\t" + option_value_hint, open_value_key

    # case 3 is when every option is implemneted
    elif length == 3:
        open_value_key, option_value_hint, option_value_value = value_elements
        return open_value_key + "\t" + option_value_hint, option_value_value

    else:
        error("unexpected length of '" + str(length) +
              "' with value elements '[" + ", ".join(value_elements) + "]'")
