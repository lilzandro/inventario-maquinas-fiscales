import customtkinter as ctk


class AppTheme:
    BACKGROUND = "#F0F4F8"
    SIDEBAR_BG = "#1A2235"
    PRIMARY = "#e89754"
    PRIMARY_DARK = "#d4864a"
    CARD = "#ffffff"
    BORDER = "#E8EDF2"
    TEXT = "#0F172A"
    TEXT_SECONDARY = "#475569"
    TEXT_MUTED = "#94A3B8"
    SUCCESS = "#16A34A"
    WARNING = "#D97706"
    DANGER = "#DC2626"
    PURPLE = "#7C3AED"


class UI_COLORS:
    BASE = "#F0F4F8"
    SIDEBAR = "#1A2235"
    TOPBAR = "#ffffff"
    SURFACE = "#ffffff"
    BG = "#F0F4F8"
    CARD = "#ffffff"
    BORDER = "#E8EDF2"
    BORDER_SUBTLE = "#F1F5F9"

    TEXT = "#0F172A"
    TEXT_ON_DARK = "#ffffff"
    TEXT_ON_LIGHT = "#0F172A"
    TEXT_SECONDARY = "#475569"
    TEXT_MUTED = "#94A3B8"
    SIDEBAR_TEXT = "#A8B4C8"

    PRIMARY = "#e89754"
    SECONDARY = "#d4864a"
    ACCENT = "#e89754"

    WHITE = "#FFFFFF"
    GRAY = "#64748B"
    GREEN = "#16A34A"
    TEAL = "#319795"
    DANGER = "#DC2626"
    PURPLE = "#7C3AED"

    STATUS_COLORS = {
        "En Stock":          "#16A34A",
        "Instalada":         "#2563EB",
        "En Mantenimiento":  "#D97706",
        "En Reparación":     "#9333EA",
        "Desincorporada":    "#DC2626",
        "Falla":             "#DC2626",
    }

    STATUS_BADGE_BG = {
        "En Stock":          "#F0FDF4",
        "Instalada":         "#EFF6FF",
        "En Mantenimiento":  "#FFFBEB",
        "En Reparación":     "#FAF5FF",
        "Desincorporada":    "#FEF2F2",
        "Falla":             "#FEF2F2",
    }

    BADGE_BG = {
        "success": "#F0FDF4",
        "warning": "#FFFBEB",
        "danger": "#FEF2F2",
        "default": "#EFF6FF",
        "neutral": "#F8FAFC",
        "purple": "#FAF5FF",
    }

    BADGE_FG = {
        "success": "#16A34A",
        "warning": "#D97706",
        "danger": "#DC2626",
        "default": "#2563EB",
        "neutral": "#64748B",
        "purple": "#7C3AED",
    }


FONT_SIZES = {
    "micro": 10,
    "tiny": 11,
    "small": 12,
    "body": 13,
    "medium": 14,
    "large": 16,
    "xlarge": 22,
    "xxlarge": 26,
    "title": 28,
}

SIZES = {
    "button_height": 36,
    "entry_height": 36,
    "header_height": 52,
    "sidebar_width": 230,
    "card_radius": 12,
    "button_radius": 8,
    "badge_radius": 20,
    "border_width": 1,
    "pad": 16,
    "pad_large": 24,
    "pad_small": 8,
    "nav_item_height": 54,
    "icon_box": 40,
}


def apply_global_theme():
    ctk.set_appearance_mode("Light")
