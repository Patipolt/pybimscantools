""" Text coloring functions """

HEX_COLOR_LIST = ["0072BD",
                  "D95319",
                  "EDB120",
                  "7E2F8E",
                  "77AC30",
                  "4DBEEE",
                  "A2142F",
                  "0072BD",
                  "D95319",
                  "EDB120",
                  "7E2F8E",
                  "77AC30",
                  "4DBEEE",
                  "A2142F",
                  "0072BD",
                  "D95319",
                  "EDB120",
                  "7E2F8E",
                  "77AC30",
                  "4DBEEE"]


def colored_text(text: str, color: str) -> str:
    """
    Colorize the given text in the given color.
    """
    colors = {
        'Red': [255, 0, 0],
        'Green': [0, 255, 0],
        'Blue': [0, 200, 255],
        'Yellow': [255, 255, 0],
        'Orange': [255, 150, 0],
        'Pink': [255, 0, 150],
        'Violet': [200, 100, 200],
        'Pale': [255, 235, 200],
        'reset': '\033[0m'
    }
    if color not in colors:
        raise ValueError(f"Color '{color}' is not supported.")
    return f"\033[38;2;{colors[color][0]};{colors[color][1]};" \
           f"{colors[color][2]}m{text}{colors['reset']}"
