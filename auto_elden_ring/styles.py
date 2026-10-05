"""Style geometry and independent palettes; RGB animation is opt-in."""

STYLES = {
    "modern": {
        "themes": ("calm", "slate", "mint"),
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
    "rainbow": {
        "themes": ("spectrum", "pastel", "prism"),
        "radius": 16,
        "button_radius": 12,
        "font": "Segoe UI",
        "sidebar": 230,
    },
}
PALETTES = {
    "calm": ("#F2F3EF", "#FFFFFF", "#E7EBE3", "#263A32", "#68756D", "#526E5D"),
    "slate": ("#171D29", "#222B3B", "#344158", "#EDF1F8", "#A5B1C6", "#536F9C"),
    "mint": ("#EAF4F0", "#FFFFFF", "#CCE5DC", "#183C34", "#4F7367", "#287565"),
    "elden": ("#161B19", "#202824", "#303C33", "#EEE9D8", "#A7B1A4", "#A18B55"),
    "ember": ("#211A18", "#302320", "#50342A", "#F6EAD8", "#C1A38E", "#A95732"),
    "moon": ("#151D2A", "#232D42", "#354564", "#F0EDE4", "#A8B9D0", "#5B77A6"),
    "xp_blue": ("#C0C0C0", "#D4D0C8", "#B9B9B9", "#000000", "#333333", "#0000FF"),
    "xp_silver": ("#EAEAF0", "#FFFFFF", "#D5D7E1", "#26263A", "#63637A", "#666898"),
    "xp_olive": ("#ECEBD9", "#FFFFF8", "#D3D9B2", "#354020", "#73785B", "#738742"),
    "spectrum": ("#17182A", "#25283E", "#39334F", "#F6F0FF", "#B8AAC9", "#8558B8"),
    "pastel": ("#F7F0FA", "#FFFFFF", "#E7DCEF", "#45324F", "#8A6F98", "#8656A6"),
    "prism": ("#E9F3FA", "#FFFFFF", "#D2E6F3", "#253950", "#698097", "#366B95"),
}
READING = ("#F6F0DE", "#FFFAED", "#E6DCC1", "#252C31", "#5B6264", "#486B69")
RAINBOW = ("#CC686E", "#CF9946", "#759A57", "#4A9F98", "#648FC0", "#A27BC2")


def appearance(state):
    style = STYLES[state["style"]]
    palette = READING if state["dyslexic"] else PALETTES[state["theme"]]
    return style, palette
