# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Run app
python main.py

# Install dependencies (use venv)
source venv/bin/activate
pip install -r requirements.txt

# Reset database (after schema changes)
rm inventario.db && python main.py

# Initialize DB standalone
python database/db_manager.py
```

No test framework, no linter configured. Verify changes by running `python main.py` and exercising the UI flow.

## Architecture

Desktop inventory management app for fiscal machines (máquinas fiscales). Python + CustomTkinter + SQLite.

**Entry point:** `main.py` → `App` (CTk root) → `LoginView` → on success → `DashboardView`

**View flow:**
- `LoginView` authenticates against `users` table, calls `on_login_success(user_info)` callback
- `DashboardView` owns a horizontal nav bar + `main_content` frame; swaps child views via `clear_content()` + lazy import instantiation
- Child views (`InventoryView`, `ClientsView`, `ServicesView`, `ReportsView`) each live in `ui/` and are self-contained `CTkFrame` subclasses

**Database:** `database/db_manager.py`
- `DB_PATH` resolves relative to the module file → always points to `inventario.db` at repo root
- `get_connection()` opens a new connection per operation — close immediately after use
- `create_tables()` is idempotent; seeds default admin (`admin` / `admin123`, PBKDF2-SHA256 hashed)
- Tables: `users`, `distributors`, `machine_models`, `clients`, `machines`, `services`
- `machines.status` must be exactly one of: `'En Stock'`, `'Instalada'`, `'En Mantenimiento'`, `'En Reparación'`, `'Desincorporada'`
- Dates stored as `YYYY-MM-DD` strings

**Theme system:** `theme.py`
- `AppTheme` — primary color constants for widgets
- `UI_COLORS` — extended palette including `STATUS_COLORS` dict and surface/text variants
- `FONT_SIZES` / `SIZES` — scaled dicts (scale factor `1.10`)
- `apply_global_theme()` sets dark mode; must be called before any widget is created (done in `main.py`)
- Always use `AppTheme`/`UI_COLORS` constants on widgets — never hardcode hex colors
- Each view defines its own local `VIEW_COLORS` dict; do not share between views

**Logging:** `utils/logger.py` exports `logger`, `log_error()`, `log_info()`. Logs rotate in `logs/app.log` (5 MB × 3 backups).

**Reports:** Excel export via `openpyxl` in `ReportsView`.

## Critical rules

- Import `DB_PATH` from `database.db_manager` — never recompute the path locally
- Unbind `<Return>` in `LoginView` on success; re-bind only if reusing the form
- After schema changes, delete `inventario.db` and restart — no migrations exist

## Reglas de comportamiento (ahorro de tokens)

1. **No programar sin contexto** — leer archivos relevantes y git log antes de escribir código. Si falta contexto, preguntar.
2. **Respuestas cortas** — 1-3 oraciones. Sin preámbulos ni resumen final. No repetir lo que dijo el usuario.
3. **No reescribir archivos completos** — usar Edit (reemplazo parcial). Write solo si cambio >80% del archivo.
4. **No releer archivos ya leídos** — si ya se leyó en esta conversación, no releer salvo que haya cambiado.
5. **Validar antes de declarar hecho** — compilar, correr tests, o verificar funcionamiento. Nunca decir "listo" sin evidencia.
6. **Cero charla aduladora** — no decir "Excelente pregunta", "Gran idea", etc. Ir directo al trabajo.
7. **Soluciones simples** — implementar lo mínimo. Sin abstracciones, helpers, ni features no pedidos.
8. **No pelear con el usuario** — si dice "hazlo así", hacerlo. Mencionar concern en 1 oración y proceder.
9. **Leer solo lo necesario** — usar offset/limit. No hacer Glob+Grep+Read cuando Read directo basta.
10. **No narrar el plan antes de ejecutar** — no describir los pasos que se van a dar. Solo ejecutar.
11. **Paralelizar tool calls** — leer múltiples archivos independientes en un solo mensaje.
12. **No duplicar código en la respuesta** — si se editó un archivo, no copiar el resultado en texto.
13. **No usar Agent cuando Grep/Read basta** — Agent solo para búsquedas amplias o tareas complejas.
