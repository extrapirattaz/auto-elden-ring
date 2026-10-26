"""Two visual styles, each with one palette, and the contrast helpers that keep them legible.

Palette order: background, paper (cards and sidebar), soft (fills), ink (text),
muted (secondary text), accent (actions and the current page), line (borders).
"""

STYLES = {
    # The base style: black text on white, Segoe UI, visible borders and no decoration.
    "readable": {
        "radius": 6,
        "button_radius": 4,
        "border": 1,
        "font": "Segoe UI",
        "display": "Segoe UI",
        "sidebar": 220,
        "current": "fill",
        "selector": "accent",
    },
    # A dark travel journal: serif headings, ruled cards and a brass accent.
    "ledger": {
        "radius": 6,
        "button_radius": 4,
        "border": 1,
        "font": "Bahnschrift",
        "display": "Constantia",
        "sidebar": 232,
        "current": "ruled",
        "selector": "tab",
    },
}
PALETTES = {
    "readable": ("#F5F6F8", "#FFFFFF", "#E8EBF0", "#0F1419", "#4B5563", "#1E40AF", "#6B7280"),
    "ledger": ("#121210", "#1B1A17", "#2A2823", "#E8DCC0", "#9C9482", "#B08D4E", "#6E675A"),
}
# Reading mode replaces either palette with a quiet cream one for dyslexic readers.
READING = ("#F6F0DE", "#FFFAED", "#E6DCC1", "#252C31", "#5B6264", "#486B69", "#7A7060")


def appearance(state):
    style = STYLES[state["style"]]
    palette = READING if state["dyslexic"] else PALETTES[state["style"]]
    return style, palette


def _luminance(color):
    channels = (int(color[index : index + 2], 16) / 255 for index in (1, 3, 5))
    linear = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in channels]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def contrast_ratio(first, second):
    lighter, darker = sorted((_luminance(first), _luminance(second)), reverse=True)
    return (lighter + 0.05) / (darker + 0.05)


def text_on_accent(accent, surface):
    """Text for accent fills: white, or the surface when white reads worse."""
    return (
        "#FFFFFF"
        if contrast_ratio("#FFFFFF", accent) >= contrast_ratio(surface, accent)
        else surface
    )


def shade(color, toward, amount):
    """Blend a color toward another by amount (0 keeps it, 1 is the target)."""
    start = bytes.fromhex(color[1:])
    end = bytes.fromhex(toward[1:])
    return "#" + "".join(f"{round(a + (b - a) * amount):02x}" for a, b in zip(start, end))


def emphasis(fill, label, amount):
    """Move a fill away from its label, so hover and press read more clearly than rest."""
    toward = "#000000" if _luminance(label) > _luminance(fill) else "#FFFFFF"
    return shade(fill, toward, amount)
