"""One palette, shared by every backend, so the two renderers are compared on
layout rather than on colour.

Restrained enterprise/federal register: near-white ground, ink-navy type, one
hue per node kind, one alarm hue reserved exclusively for repair. Nothing else
in the picture is allowed to be crimson — that is what makes a back-edge
findable in a glance.
"""

INK = "#0F172A"        # titles
INK_SOFT = "#475569"   # purpose gist
INK_FAINT = "#94A3B8"  # budget chip, axis type
PAPER = "#FFFFFF"
GROUND = "#F7F9FB"
HAIRLINE = "#E2E8F0"

KIND = {
    "agent": {"accent": "#3B4CCA", "tint": "#EEF0FE", "label": "AGENT"},
    "tool":  {"accent": "#0E7490", "tint": "#E4F3F6", "label": "TOOL"},
    "gate":  {"accent": "#7C3AED", "tint": "#F2ECFE", "label": "GATE"},
    "repair": {"accent": "#B91C1C", "tint": "#FDECEC", "label": "REPAIR"},
}

EDGE = {
    "sequential":  {"color": "#64748B", "width": 1.6, "dash": None,   "label": "sequential"},
    "conditional": {"color": "#15803D", "width": 1.6, "dash": None,   "label": "conditional — fires on pass"},
    "parallel":    {"color": "#0891B2", "width": 1.6, "dash": "1 3",  "label": "parallel fan-out"},
    "repair":      {"color": "#DC2626", "width": 1.8, "dash": "6 3",  "label": "repair back-edge"},
}

# Stage band tints, S0 .. S7. Deliberately low-chroma: the band says "where am
# I", the node says "what is this". If the band competes with the node it wins,
# and then the diagram is about stages instead of about work.
STAGE_TINTS = [
    "#F1F5F9", "#EEF2F7", "#F1F5F9", "#EEF2F7",
    "#F1F5F9", "#EEF2F7", "#F1F5F9", "#EEF2F7",
]

STAGE_TITLES = {
    "S0": "Contract & profile",
    "S1": "Resource discovery",
    "S2": "Evidence & semantics",
    "S3": "Outline & design",
    "S4": "Native composition",
    "S5": "Render & inspect",
    "S6": "Review & repair",
    "S7": "Contract closure",
}

FONT = "Helvetica"          # Graphviz name
FONT_CSS = "'Inter', 'Helvetica Neue', Helvetica, Arial, sans-serif"
