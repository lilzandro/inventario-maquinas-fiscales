# Variante C — `MaquinaCardDetail` (Preview / Detalle)

## Tecnologías

- Python 3.12
- CustomTkinter (`>=5.2.0`)
- Pillow (`PIL`) — renderizado de texto rotado
- Tkinter Canvas — dibujo de formas con bordes redondeados asimétricos

## Dependencias

```txt
customtkinter>=5.2.0
Pillow
```

## Estructura Visual

```
┌─────────────────────────────────────────────────┐
│ ╔══╗  Brand · Model                      ⊖  ✎  │
│ ║📦║  Empresa · RIF V-XXXXXXXX                │
│ ║EN║  ────────────────────────────────────     │
│ ║  ║  ┌──────────┐  ┌──────────────┐          │
│ ║ST║  │ N° Serial │  │ Reg. SENIAT  │          │
│ ║OC║  │ AF123456  │  │ SEN-2024-001 │          │
│ ║K ║  └──────────┘  └──────────────┘          │
│ ╚══╝                                           │
└─────────────────────────────────────────────────┘
```

Tarjeta vertical de **200px de alto**. Para destacar un registro individual.

## Contrato

```python
MaquinaCardDetail(parent, data, on_edit=None, on_decomm=None, on_delete=None)

# data: dict con claves:
#   company, rif, brand, model, serial, seniat, status
```

## Implementación Paso a Paso

### 1. Imports

```python
import tkinter as tk
from PIL import Image, ImageDraw, ImageFont, ImageTk

import customtkinter as ctk
from theme import COLORS, STATUS, FONT_SANS, FONT_MONO
from widgets import TextButton, IconButton
```

### 2. Tarjeta base

```python
class MaquinaCardDetail(ctk.CTkFrame):
    HEIGHT = 200

    def __init__(self, parent, data, on_edit=None, on_decomm=None, on_delete=None):
        s = STATUS[data["status"]]
        super().__init__(
            parent,
            fg_color=COLORS["paper"],
            corner_radius=10,
            border_width=1,
            border_color=COLORS["ink_200"],
            height=self.HEIGHT,
        )
        self.grid_propagate(False)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
```

### 3. Banda lateral izquierda con Canvas

La banda tiene **bordes redondeados solo del lado izquierdo**, dibujados con primitivas de Canvas.

```python
r = 10     # radio de esquina
w = 58     # ancho de banda
h = self.HEIGHT

band = tk.Canvas(self, width=w, highlightthickness=0)
band.grid(row=0, column=0, sticky="nsew")

# Cuerpo principal
band.create_rectangle(r, 0, w, h, fill=s["strip"], outline="", width=0)

# Relleno entre curvas (lado izquierdo)
band.create_rectangle(0, r, r, h - r, fill=s["strip"], outline="", width=0)

# Esquina superior izquierda
band.create_arc(
    0, 0, 2 * r, 2 * r, start=90, extent=90,
    fill=s["strip"], outline="", width=0,
)

# Esquina inferior izquierda
band.create_arc(
    0, h - 2 * r, 2 * r, h, start=180, extent=90,
    fill=s["strip"], outline="", width=0,
)
```

#### Explicación del dibujo

| Primitiva | Función |
|-----------|---------|
| `create_rectangle(r, 0, w, h)` | Cuerpo principal (excepto el borde izquierdo) |
| `create_rectangle(0, r, r, h-r)` | Rellena la franja izquierda entre las dos esquinas |
| `create_arc(0,0,2r,2r) start=90, extent=90` | Quarter-circle: esquina top-left |
| `create_arc(0,h-2r,2r,h) start=180, extent=90` | Quarter-circle: esquina bottom-left |

### 4. Icono de estado en la banda

```python
band.create_text(29, 22, text=s["icon"], fill="white",
                 font=(FONT_SANS, 20), anchor="center")
```

### 5. Texto rotado 90° (lectura abajo→arriba)

Renderizar el texto con Pillow, rotarlo y mostrarlo como imagen en el Canvas.

```python
label_str = s["label"].upper()

# Cargar fuente (fallback a default si no existe el archivo)
try:
    _font = ImageFont.truetype(
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 10)
except (IOError, OSError):
    _font = ImageFont.load_default()

# Renderizar texto horizontal
bbox = _font.getbbox(label_str)
tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
img = Image.new("RGBA", (tw + 8, th + 8), s["strip"])
draw = ImageDraw.Draw(img)
draw.text((4, 4), label_str, fill="white", font=_font)

# Rotar 90° y mostrar
rotated = img.rotate(90, expand=True)
photo = ImageTk.PhotoImage(rotated)

band.create_image(29, 115, image=photo, anchor="center")
band.image = photo   # ← ¡IMPORTANTE! mantener referencia para evitar GC
```

#### Notas sobre la fuente PIL

- **Windows**: usar `"Segoe UI.ttf"` para coincidir con `FONT_SANS`
- **Linux**: `"DejaVuSans-Bold.ttf"` (ruta: `/usr/share/fonts/truetype/dejavu/`)
- **macOS**: `"SFNSDisplay.ttf"` o instalar IBM Plex Sans
- Siempre envolver en `try/except` con `ImageFont.load_default()` como fallback

### 6. Contenido (lado derecho)

```python
content = ctk.CTkFrame(self, fg_color="transparent")
content.grid(row=0, column=1, sticky="nsew", padx=18, pady=14)
content.grid_columnconfigure(0, weight=1)
```

### 7. Fila superior: título + acciones

```python
top = ctk.CTkFrame(content, fg_color="transparent")
top.grid(row=0, column=0, sticky="ew")
top.grid_columnconfigure(0, weight=1)

title_block = ctk.CTkFrame(top, fg_color="transparent")
title_block.grid(row=0, column=0, sticky="w")

# Brand · Model
title_row = ctk.CTkFrame(title_block, fg_color="transparent")
title_row.pack(anchor="w")
ctk.CTkLabel(title_row, text=data["brand"],
    font=(FONT_SANS, 18, "bold"), text_color=COLORS["ink_900"],
).pack(side="left")
ctk.CTkLabel(title_row, text="·",
    font=(FONT_SANS, 18), text_color=COLORS["ink_300"],
).pack(side="left", padx=8)
ctk.CTkLabel(title_row, text=data["model"],
    font=(FONT_SANS, 18), text_color=COLORS["ink_700"],
).pack(side="left")

# Empresa · RIF
ctk.CTkLabel(title_block,
    text=f"{data['company']}   ·   RIF {data['rif']}",
    font=(FONT_SANS, 11), text_color=COLORS["ink_500"],
).pack(anchor="w", pady=(2, 0))

# Acciones
actions = ctk.CTkFrame(top, fg_color="transparent")
actions.grid(row=0, column=1, sticky="e")
TextButton(actions, "edit",   command=on_edit).pack(side="left", padx=3)
TextButton(actions, "decomm", command=on_decomm).pack(side="left", padx=3)
IconButton(actions, "delete", command=on_delete).pack(side="left", padx=3)
```

### 8. Divisor

```python
divider = ctk.CTkFrame(content, fg_color=COLORS["ink_100"], height=1)
divider.grid(row=1, column=0, sticky="ew", pady=(10, 12))
```

### 9. Meta: Serial + SENIAT (bloques)

Dos bloques independientes en grid 50/50 con fondo sutil.

```python
meta = ctk.CTkFrame(content, fg_color="transparent")
meta.grid(row=2, column=0, sticky="ew")
meta.grid_columnconfigure(0, weight=1, minsize=120)
meta.grid_columnconfigure(1, weight=1)

self._meta_block(meta, 0, "N° Serial", data["serial"])
self._meta_block(meta, 1, "Reg. SENIAT", data["seniat"])
```

Helper `_meta_block`:

```python
@staticmethod
def _meta_block(parent, col, label, value):
    f = ctk.CTkFrame(parent, fg_color=COLORS["ink_50"], corner_radius=8)
    f.grid(row=0, column=col, sticky="ew", padx=(0, 10) if col == 0 else 0)
    ctk.CTkLabel(f, text=label,
        font=(FONT_SANS, 9, "bold"), text_color=COLORS["ink_500"],
    ).pack(anchor="w", padx=12, pady=(8, 0))
    ctk.CTkLabel(f, text=value,
        font=(FONT_MONO, 13, "bold"), text_color=COLORS["ink_900"],
    ).pack(anchor="w", padx=12, pady=(0, 8))
    return f
```

## Helpers Necesarios

### `TextButton` (`widgets.py`)

```python
class TextButton(ctk.CTkButton):
    def __init__(self, parent, kind="edit", command=None):
        a = ACTIONS[kind]
        super().__init__(parent,
            text=f"{a['icon']}  {a['label']}", height=28, corner_radius=7,
            fg_color=COLORS["paper"], text_color=COLORS["ink_700"],
            hover_color=a["hover_bg"], border_width=1,
            border_color=COLORS["ink_200"], font=(FONT_SANS, 11),
            command=command,
        )
```

### `IconButton` (`widgets.py`)

```python
class IconButton(ctk.CTkButton):
    def __init__(self, parent, kind="edit", command=None):
        a = ACTIONS[kind]
        super().__init__(parent,
            text=a["icon"], width=28, height=28, corner_radius=7,
            fg_color=COLORS["paper"], text_color=COLORS["ink_500"],
            hover_color=a["hover_bg"], border_width=1,
            border_color=COLORS["ink_200"], font=(FONT_SANS, 13),
            command=command,
        )
```

## Sistema de Tokens (`theme.py`)

```python
COLORS = {
    "paper":   "#ffffff",
    "ink_900": "#14202e",
    "ink_700": "#38465c",
    "ink_500": "#6b7a92",
    "ink_300": "#b6bfcf",
    "ink_200": "#d7dde8",
    "ink_100": "#eaeef5",
    "ink_50":  "#f5f7fb",
}

STATUS = {
    "stock":     {"label": "En Stock",      "strip": "#1ea255", "icon": "📦"},
    "assigned":  {"label": "Asignada",      "strip": "#2d83d8", "icon": "🏢"},
    "maint":     {"label": "Mantenimiento", "strip": "#e09011", "icon": "🔧"},
    "repair":    {"label": "En Reparación", "strip": "#7c5dd0", "icon": "🛠"},
    "decomm":    {"label": "Desincorporada","strip": "#8a98ad", "icon": "⏻"},
}

ACTIONS = {
    "edit":   {"icon": "✎", "label": "Editar", "hover_bg": "#e0eefb", "hover_fg": "#1d6fc4"},
    "decomm": {"icon": "⊘", "label": "Desincorporar", "hover_bg": "#fcecd0", "hover_fg": "#b97208"},
    "delete": {"icon": "🗑", "label": "Eliminar", "hover_bg": "#fbdcdb", "hover_fg": "#c1322f"},
}

FONT_SANS = "Segoe UI"
FONT_MONO = "Consolas"
```

## Buenas Prácticas

1. **`grid_propagate(False)`** en la tarjeta para mantener altura fija.
2. **Referencia a PhotoImage**: asignar a `band.image = photo` para evitar que el garbage collector elimine la imagen.
3. **Fuente PIL**: siempre con `try/except` → `ImageFont.load_default()` como fallback.
4. **Padding consistente**: `content.pady=14` + `_meta_block` pady interno suman 14 para alineación visual.
5. **Canvas `highlightthickness=0`** para eliminar borde adicional alrededor del Canvas.
