# AGENTS.md

## SistemaInventario - Sistema de Gestión de Máquinas Fiscales

### Stack & Configuración
- **App de escritorio Python** con CustomTkinter; ejecutar vía `python main.py`
- **SQLite** en `inventario.db` (raíz); `database/db_manager.py` crea tablas automáticamente en primer `import`
- **Dependencias**: `customtkinter`, `openpyxl`, `pillow` (ver `requirements.txt`)
- Instalar desde `requirements.txt` y asegurar que `inventario.db` exista antes de correr (la inicialización de BD ocurre en la primera llamada a `create_tables()`)

### Sistema de Temas (Importante para UI)
- **AppTheme** en `theme.py` define constantes de color globales:
  - `BACKGROUND = "#1f1f20"` (fondo principal)
  - `PRIMARY = "#2b4c7e"` (color primario botones)
  - `SECONDARY = "#567ebb"` (color secundario/hover)
  - `BORDER = "#606d80"` (bordes/detalles)
  - `TEXT = "#dce0e6"` (texto y contrastes)
- **apply_global_theme()** configura el modo oscuro
- **Llamar a apply_global_theme()** antes de crear cualquier widget (ver `main.py`)
- **Los widgets deben usar las constantes de AppTheme explícitamente**:
  - `ctk.CTkFrame(fg_color=AppTheme.BACKGROUND)`
  - `ctk.CTkButton(fg_color=AppTheme.PRIMARY, hover_color=AppTheme.SECONDARY)`
  - `ctk.CTkEntry(border_color=AppTheme.BORDER, text_color=AppTheme.TEXT)`
  - `ctk.CTkLabel(text_color=AppTheme.TEXT)`
- Los widgets heredan estos colores por configuración de clase; no usar colores hardcodeados
- Cada vista mantiene su propio diccionario `COLORS` para estilos específicos (no compartir entre vistas)

### Seguridad (Mejoras implementadas)
- **Contraseñas hasheadas** con PBKDF2-SHA256 (funciones `hash_password` / `verify_password` en `db_manager.py`)
- Admin por defecto `admin/admin123` — la contraseña ahora se almacena con hash, no texto plano

### Esquema de Base de Datos
Tablas: `users`, `distributors`, `machine_models`, `clients`, `machines`, `services`
- `machines.status` ∈ `'En Stock'`, `'Instalada'`, `'Desincorporada'`
- Todas las fechas se almacenan como cadenas `YYYY-MM-DD`; usar `IFNULL` para campos SQLite anulables
- Integridad referencial: FKs con `ON DELETE SET NULL` (máquinas) y `ON DELETE CASCADE` (servicios)
- Admin por defecto: `admin` con contraseña hasheada

### Acceso a Datos Centralizado
- **Todas las vistas usan `DB_PATH` desde `database.db_manager`** (no recomputar localmente); importar `from database.db_manager import DB_PATH`
- Funciones de utilidad: `hash_password()`, `verify_password()`, `get_connection()`, `create_tables()` en `db_manager.py`

### Arquitectura de Vistas (Crítico)
- Las vistas heredan `ctk.CTkFrame`, se empaquetan con `fill='both', expand=True` o posicionamiento explícito
- Cada vista mantiene su propio diccionario `COLORS` — no compartir constantes entre vistas
- `DashboardView` orquesta vistas hijas mediante `clear_content()` (destruye actual) + instanciación; no hay estado compartido entre vistas
- El login desvincula la tecla `<Return>` mediante `self.master.unbind("<Return>")` al éxito; volver a vincular si se reutiliza el formulario de login

### Flujo de Ejecución
1. `python main.py` → `App()` → `show_login()` → `LoginView`
2. Éxito: `DashboardView` + callback `on_logout` hacia `show_login()` (destruye vista previa)
3. Botones del dashboard instancian vistas perezosamente; cada vista carga sus propios datos de referencia desde BD

### Patrones de Código a Preservar
- Conexiones SQLite abiertas por operación (`get_connection()`), cerradas inmediatamente
- Enlaces UI usan `command=` con lambdas o métodos enlazados; evitar cierres inline que capturen estado obsoleto
- Patrón `clear_content()` = `self.current_view.destroy()` antes del reemplazo
- Exportación de reportes usa `openpyxl`; verificar que el nombre de la hoja coincida con lo que espera el llamador
- Validar inputs (RUT básico, teléfono) antes de operaciones de BD

### Validación
- Sin frameworks de test/lint/type configurados
- Verificar cambios ejecutando `python main.py` y ejercitando el flujo UI (login → dashboard → subvistas)
- Tras cambios de esquema de BD, eliminar `inventario.db` y reiniciar para regenerar vía `create_tables()`

### Errores Comunes a Evitar
- No centralizar `DB_PATH` — usar el import desde `database.db_manager`
- No compartir `COLORS` o constantes entre vistas — cada vista define las suyas
- No asumir que `inventario.db` existe — verificar presencia o llamar `create_tables()` si se inicializa desde cero
- Re-vincular `<Return>` sin desvincular previamente causa intentos de login duplicados
- Modificar valores de estado de máquina rompe filtros posteriores — usar exactamente los strings enumerados
- **No hardcodear colores en widgets** — usar `AppTheme` y aplicar explícitamente las constantes al crear widgets