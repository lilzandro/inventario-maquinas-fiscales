# AGENTS.md

## SistemaInventario - Fiscal Machine Management System

### Stack
- Python desktop app using **CustomTkinter**
- **SQLite** database (`inventario.db`)
- Dependencies: `customtkinter`, `openpyxl`, `pillow`

### Running the App
```bash
python main.py
```

### Entry Points
- `main.py` - App entry point, initializes CTk window and view switching
- `ui/` - All view modules (login_view, dashboard_view, inventory_view, etc.)
- `database/db_manager.py` - DB initialization and schema

### Database
- SQLite at `inventario.db` (root directory)
- Tables: `users`, `distributors`, `machine_models`, `clients`, `machines`, `services`
- DB schema created on first import via `create_tables()`
- Default admin: `admin` / `admin123` (plain text password)

### Architecture Notes
- Each UI module computes `DB_PATH` independently using `os.path.dirname(os.path.abspath(__file__))`
- Views inherit from `ctk.CTkFrame` and manage their own layout
- `DashboardView` orchestrates view switching via `clear_content()` + view instantiation
- Excel export uses `openpyxl` in `reports_view.py`

### No Test/Lint Setup
- No pytest, tox, or test framework configured
- No type checking (mypy), linting (ruff/pylint), or pre-commit hooks
- Verify changes manually by running `python main.py`

### Important Conventions
- Use `IFNULL` in SQLite queries for nullable fields
- Service dates stored as `YYYY-MM-DD` strings
- Machine statuses: `'En Stock'`, `'Instalada'`, `'Desincorporada'`
- Login binds `<Return>` key and unbinds on success
