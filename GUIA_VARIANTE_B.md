# Variante B — `MaquinaCardCompact` (Lista Densa)

## Tecnologías

- Python 3.12
- CustomTkinter (`>=5.2.0`)
- Pillow (para `CTkImage` si se usan imágenes en Avatar)

## Dependencias

```txt
customtkinter>=5.2.0
Pillow
```

## Estructura Visual

```
┌──────────────────────────────────────────────────────────────────┐
│ ██  Avatar  Empresa+RIF  Marca·Modelo  Serial  SENIAT  ◉  📝⊘🗑 │
└──────────────────────────────────────────────────────────────────┘
  4px stripe                                        chip   acciones
```

Una sola fila horizontal de **64px de alto**. Ideal para listar 10+ registros.

## Contrato

```python
MaquinaCardCompact(parent, data, on_edit=None, on_decomm=None, on_delete=None)

# data: dict con claves:
#   company, rif, brand, model, serial, seniat, status
```

## Implementación Paso a Paso

### 1. Tarjeta base

```python
import customtkinter as ctk
from theme import COLORS, STATUS, FONT_SANS, FONT_MONO
from widgets import Avatar, StatusChip, IconButton, labeled_field

class MaquinaCardCompact(ctk.CTkFrame):
    HEIGHT = 64

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
```

### 2. Banda lateral (stripe de estado)

```python
stripe = ctk.CTkFrame(
    self, fg_color=s["strip"], width=4, corner_radius=0,
)
stripe.grid(row=0, column=0, sticky="ns")
```

### 3. Contenedor de contenido

Usar `grid` con columnas de ancho fijo. La última columna (acciones) se pega a la derecha.

```python
content = ctk.CTkFrame(self, fg_color="transparent")
content.grid(row=0, column=1, sticky="nsew", padx=(14, 12), pady=8)
content.grid_columnconfigure(1, minsize=190)   # empresa
content.grid_columnconfigure(2, minsize=170)   # marca·modelo
content.grid_columnconfigure(3, minsize=120)   # serial
content.grid_columnconfigure(4, minsize=130)   # seniat
content.grid_columnconfigure(5, weight=1)      # espaciador elástico
```

### 4. Avatar

```python
Avatar(content, data["company"]).grid(row=0, column=0, padx=(0, 12), sticky="w")
```

### 5. Empresa + RIF (stack vertical)

```python
comp = ctk.CTkFrame(content, fg_color="transparent")
comp.grid(row=0, column=1, sticky="w")
ctk.CTkLabel(
    comp, text=data["company"],
    font=(FONT_SANS, 12, "bold"),
    text_color=COLORS["ink_900"], anchor="w",
).pack(anchor="w")
ctk.CTkLabel(
    comp, text=f"RIF · {data['rif']}",
    font=(FONT_SANS, 10),
    text_color=COLORS["ink_500"], anchor="w",
).pack(anchor="w")
```

### 6. Campos etiquetados

Usar el helper `labeled_field(label, value, mono=True/False)` que crea una mini columna label arriba + valor abajo.

```python
labeled_field(content, "Marca · Modelo",
    f"{data['brand']} · {data['model']}",
).grid(row=0, column=2, sticky="w", padx=(0, 16))

labeled_field(content, "N° Serial", data["serial"], mono=True,
).grid(row=0, column=3, sticky="w", padx=(0, 16))

labeled_field(content, "Reg. SENIAT", data["seniat"], mono=True,
).grid(row=0, column=4, sticky="w", padx=(0, 16))
```

### 7. Chip de estado + acciones

```python
StatusChip(content, data["status"]).grid(row=0, column=6, padx=10)

actions = ctk.CTkFrame(content, fg_color="transparent")
actions.grid(row=0, column=7, sticky="e")
IconButton(actions, "edit",   command=on_edit).pack(side="left", padx=2)
IconButton(actions, "decomm", command=on_decomm).pack(side="left", padx=2)
IconButton(actions, "delete", command=on_delete).pack(side="left", padx=2)
```

## Helpers Necesarios

### `labeled_field` (`widgets.py`)

```python
def labeled_field(parent, label, value, mono=False):
    f = ctk.CTkFrame(parent, fg_color="transparent")
    ctk.CTkLabel(f, text=label.upper(),
        font=(FONT_SANS, 9, "bold"),
        text_color=COLORS["ink_500"], anchor="w",
    ).pack(anchor="w")
    ctk.CTkLabel(f, text=value,
        font=(FONT_MONO if mono else FONT_SANS, 12, "bold"),
        text_color=COLORS["ink_900"], anchor="w",
    ).pack(anchor="w")
    return f
```

### `Avatar` (`widgets.py`)

```python
class Avatar(ctk.CTkFrame):
    def __init__(self, parent, name, size=32):
        super().__init__(parent, width=size, height=size,
            corner_radius=8, fg_color="#3d537a")
        self.pack_propagate(False)
        initials = "".join(w[0] for w in name.split()[:2]).upper()
        ctk.CTkLabel(self, text=initials or "?",
            text_color="white", font=(FONT_SANS, 11, "bold"),
        ).place(relx=0.5, rely=0.5, anchor="center")
```

### `StatusChip` (`widgets.py`)

```python
class StatusChip(ctk.CTkFrame):
    def __init__(self, parent, status_key):
        s = STATUS[status_key]
        super().__init__(parent, fg_color=s["chip_bg"], corner_radius=6)
        ctk.CTkLabel(self, text=s["label"],
            text_color=s["chip_fg"], font=(FONT_SANS, 10, "bold"),
        ).pack(padx=10, pady=3)
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

## Buenas Prácticas

- **`grid_propagate(False)`** en la tarjeta para mantener altura fija de 64px.
- **`sticky="ns"`** en la stripe para que se estire al alto completo.
- **Columna elástica** (`weight=1`) entre SENIAT y el chip para que las acciones se mantengan a la derecha.
- **Callbacks opcionales** (`None` por defecto) para reutilizar la tarjeta sin manejadores.

## Sistema de Tokens (`theme.py`)

```python
COLORS = {
    "paper":   "#ffffff",
    "ink_900": "#14202e",
    "ink_700": "#38465c",
    "ink_500": "#6b7a92",
    "ink_200": "#d7dde8",
}

STATUS = {
    "stock":     {"label": "En Stock",      "strip": "#1ea255", ...},
    "assigned":  {"label": "Asignada",      "strip": "#2d83d8", ...},
    "maint":     {"label": "Mantenimiento", "strip": "#e09011", ...},
    "repair":    {"label": "En Reparación", "strip": "#7c5dd0", ...},
    "decomm":    {"label": "Desincorporada","strip": "#8a98ad", ...},
}

ACTIONS = {
    "edit":   {"icon": "✎", "hover_bg": "#e0eefb", "hover_fg": "#1d6fc4"},
    "decomm": {"icon": "⊘", "hover_bg": "#fcecd0", "hover_fg": "#b97208"},
    "delete": {"icon": "🗑", "hover_bg": "#fbdcdb", "hover_fg": "#c1322f"},
}

FONT_SANS = "Segoe UI"
FONT_MONO = "Consolas"
```
