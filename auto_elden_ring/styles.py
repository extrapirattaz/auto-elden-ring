"""Static styles and a small set of independent color palettes."""

STYLES = {
    "modern": {
        "themes": ("calm", "slate"),
        "radius": 14,
        "button_radius": 9,
        "font": "Segoe UI",
        "sidebar": 220,
    },
    "elden": {
        "themes": ("elden", "ember", "moon"),
        "radius": 3,
        "button_radius": 2,
        "font": "Georgia",
        "sidebar": 250,
    },
    "xp": {
        "themes": ("xp_blue",),
        "radius": 0,
        "button_radius": 0,
        "font": "Tahoma",
        "sidebar": 195,
    },
}
PALETTES = {
    "calm": ("#F2F3EF", "#FFFFFF", "#E7EBE3", "#263A32", "#68756D", "#526E5D"),
    "slate": ("#17191D", "#22252B", "#343941", "#EDF1F8", "#A5ADBA", "#526F9C"),
    "elden": ("#161B19", "#202824", "#303C33", "#EEE9D8", "#A7B1A4", "#A18B55"),
    "ember": ("#211A18", "#302320", "#50342A", "#F6EAD8", "#C1A38E", "#A95732"),
    "moon": ("#151D2A", "#232D42", "#354564", "#F0EDE4", "#A8B9D0", "#5B77A6"),
    "xp_blue": ("#C0C0C0", "#D4D0C8", "#B9B9B9", "#000000", "#333333", "#0000FF"),
}
READING = ("#F6F0DE", "#FFFAED", "#E6DCC1", "#252C31", "#5B6264", "#486B69")


def appearance(state):
    style = STYLES[state["style"]]
    palette = READING if state["dyslexic"] else PALETTES[state["theme"]]
    return style, palette
