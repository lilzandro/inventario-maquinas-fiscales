# Handoff: Sistema de Gestión de Inventario y Máquinas Fiscales

## Overview
Sistema de escritorio para gestión integral de inventario de productos, administración y servicios de máquinas fiscales. Incluye módulos de clientes, proveedores, órdenes de servicio técnico, reportes y administración de usuarios.

El sistema fue diseñado como referencia visual para ser implementado en **Python con CustomTkinter**, replicando la experiencia de una aplicación de escritorio moderna.

---

## Sobre los Archivos de Diseño
Los archivos en este paquete son **prototipos de referencia creados en HTML/React**. No son código de producción — son maquetas de alta fidelidad que muestran el aspecto visual y el comportamiento esperado de cada módulo. La tarea del desarrollador es **recrear estos diseños en Python usando CustomTkinter** (u otro framework de escritorio según convenga), respetando la estructura, colores, tipografía e interacciones definidas aquí.

**Abrir en navegador:** `Sistema de Gestion.html` — funciona directamente en el navegador sin servidor.

---

## Fidelidad
**Alta fidelidad (hifi)** — Los prototipos incluyen colores exactos, tipografía, espaciado, estados hover/activo, modales, tablas con CRUD, gráficos, kanban de servicios, y navegación lateral completamente funcional. El desarrollador debe recrear la UI de forma pixel-perfect usando las librerías disponibles en Python/CustomTkinter.

---

## Design Tokens

### Colores
| Token | Hex | Uso |
|---|---|---|
| `accent` | `#e89754` | Color principal, botones primarios, sidebar activo, iconos destacados |
| `accent-dark` | `#d4864a` | Hover sobre elementos accent |
| `sidebar-bg` | `#1A2235` | Fondo del sidebar |
| `sidebar-text` | `rgba(255,255,255,0.65)` | Texto de nav inactivo |
| `sidebar-active-text` | `#ffffff` | Texto de nav activo |
| `content-bg` | `#F0F4F8` | Fondo general del contenido |
| `card-bg` | `#ffffff` | Fondo de tarjetas/paneles |
| `border` | `#E8EDF2` | Bordes de tarjetas y tablas |
| `border-subtle` | `#F1F5F9` | Separadores sutiles |
| `text-primary` | `#0F172A` | Texto principal |
| `text-secondary` | `#475569` | Texto secundario |
| `text-muted` | `#94A3B8` | Texto atenuado/labels |
| `success` | `#16A34A` | Estados positivos, activo |
| `warning` | `#D97706` | Alertas, en proceso |
| `danger` | `#DC2626` | Errores, stock agotado |
| `purple` | `#7C3AED` | Rol administrador, KPI especial |

### Badges / Etiquetas
| Variante | Fondo | Texto | Borde |
|---|---|---|---|
| default (azul) | `#EFF6FF` | `#2563EB` | `#BFDBFE` |
| success | `#F0FDF4` | `#16A34A` | `#BBF7D0` |
| warning | `#FFFBEB` | `#D97706` | `#FDE68A` |
| danger | `#FEF2F2` | `#DC2626` | `#FECACA` |
| neutral | `#F8FAFC` | `#64748B` | `#E2E8F0` |
| purple | `#FAF5FF` | `#7C3AED` | `#E9D5FF` |

### Tipografía
- **Familia:** `Segoe UI` (preferida en Windows), fallback `system-ui, -apple-system, sans-serif`
- **Tamaños:** 10px (micro), 11px (labels/badges), 12px (tabla headers), 13px (cuerpo), 14px (subtítulos), 16px (títulos sección), 22px (page title), 26px (stat values)
- **Pesos:** 400 (normal), 600 (semibold), 700 (bold), 800 (extrabold logo)

### Espaciado
- Padding de página: `24px 28px`
- Gap entre stat cards: `16px`
- Padding tarjeta: `20px 22px`
- Border radius tarjeta: `12px`
- Border radius botón: `8px`
- Border radius badge: `20px` (pill)
- Border radius input: `8px`

### Sombras
- Tarjeta: `0 1px 4px rgba(0,0,0,0.05)`
- Modal: `0 20px 60px rgba(0,0,0,0.2)`

---

## Layout General

```
┌─────────────────────────────────────────────────────┐
│  SIDEBAR (230px)  │  TOPBAR (52px altura)           │
│  fondo #1A2235    ├─────────────────────────────────┤
│                   │                                  │
│  Logo (32px icon) │  CONTENT AREA                   │
│                   │  fondo #F0F4F8                   │
│  Nav items        │  padding: 24px 28px              │
│  (gap 2px)        │                                  │
│                   │  PageHeader                      │
│                   │  Stat Cards (grid 4 cols)        │
│                   │  Contenido del módulo            │
│                   │                                  │
│  [Logout]         │                                  │
└─────────────────────────────────────────────────────┘
```

**Sidebar colapsado:** 64px de ancho, solo iconos centrados.

---

## Módulos / Pantallas

### 1. Dashboard
**Propósito:** Resumen ejecutivo del sistema.

**Layout:**
- 4 Stat Cards en fila (grid 4 columnas, gap 16px), mb 24px
- Sección de gráficos (2 variantes disponibles)
- 2 listas en la parte inferior (grid 2 columnas)

**Stat Cards:**
- Fondo blanco, border radius 12px, border `#E8EDF2`
- Ícono en cuadro 40×40px, border radius 10px
- Valor: 26px, bold, `#0F172A`
- Label: 12px, `#94A3B8`
- Delta: 11px, verde `#16A34A` o rojo `#DC2626`

**Variante A** (Línea + Estado Máquinas):
- Gráfico de línea izquierda (2/3 ancho) + barras de progreso estado máquinas (1/3)

**Variante B** (3 métricas con mini barras):
- 3 tarjetas iguales con valor grande + gráfico de barras pequeño (48px alto)

**Variante C** (Gradiente + KPIs):
- Tarjeta gradiente accent→`#3A7FC1` con gráfico de línea blanco + grid 2×2 de KPIs pequeños

**Lista Servicios Recientes:**
- Items con ícono 36×36px (border radius 8px), nombre, descripción truncada, badge de estado
- Separados por `border-bottom: 1px solid #F1F5F9`

**Lista Alertas de Stock:**
- Misma estructura, badge "Agotado" (danger) o "Stock bajo" (warning)

---

### 2. Inventario de Productos
**Propósito:** CRUD de productos con control de stock.

**4 Stat Cards:** Total, Normal, Stock Bajo, Agotados

**Barra de herramientas:**
- SearchBar (max-width 320px) + botones Filtrar/Exportar

**Tabla:**
| Columna | Ancho aprox | Notas |
|---|---|---|
| Código SKU | 90px | monospace, color muted |
| Producto | flex | bold |
| Stock | 70px | color semáforo: verde/naranja/rojo |
| Mínimo | 60px | |
| Precio | 80px | prefijo $ |
| Proveedor | 130px | |
| Estado | 100px | Badge |
| Acciones | 80px | íconos editar/eliminar |

**Colores de stock:**
- `> min` → `#16A34A` (verde)
- `<= min y > 0` → `#D97706` (naranja)
- `= 0` → `#DC2626` (rojo)

**Modal Nuevo/Editar Producto:**
- Grid 2 columnas para: Código+Proveedor, luego Nombre full width, luego Stock+Mínimo+Precio en 3 cols

---

### 3. Máquinas Fiscales
**Propósito:** Registro y seguimiento de máquinas fiscales por cliente.

**3 Stat Cards:** Activas / En Reparación / Dadas de Baja

**Filtros de estado** (botones tipo pill activos con color accent):
- Todas / Activas / En Reparación / Dadas de Baja

**Tabla:**
| Columna | Notas |
|---|---|
| ID | monospace |
| Modelo | bold |
| N° Serie | monospace, pequeño |
| Cliente | |
| Último Serv. | fecha |
| Próx. Serv. | fecha |
| Estado | Badge (success/warning/danger) |
| Acciones | ver/editar/eliminar |

**Modal Detalle (ver):**
- Grid 2×3 de tarjetas de info (fondo `#F8FAFC`, border radius 8px)
- Sección historial de servicios debajo

**Estados y badges:**
- `activa` → Badge success "Activa"
- `en_reparacion` → Badge warning "En Reparación"
- `dada_de_baja` → Badge danger "Dada de Baja"

---

### 4. Órdenes de Servicio Técnico
**Propósito:** Gestión del flujo completo de servicios técnicos.

**Flujo de estados (4 pasos):**
```
Pendiente → Asignada → En Proceso → Completada
```

**4 Stat Cards:** una por estado, con color correspondiente.

**Vista Kanban** (4 columnas, una por estado):
- Header coloreado por estado (rojo/naranja/azul/verde)
- Tarjetas clickeables: ID (monospace), cliente (bold), descripción truncada, badge prioridad, ID máquina + fecha
- Fondo tarjeta: `#F8FAFC`

**Tabla resumen** debajo del kanban con todas las órdenes.

**Modal Detalle:**
- Componente `StatusSteps` (barra de progreso con círculos numerados)
  - Completado: fondo `#16A34A`, ícono check blanco
  - Actual: fondo accent
  - Pendiente: fondo `#E2E8F0`
  - Línea conectora: 2px, verde si completada, gris si pendiente
- Grid 2×3 de info
- Botón "Avanzar a: [siguiente estado]" — al hacer clic avanza el estado

**Prioridades:**
- `alta` → Badge danger
- `media` → Badge warning
- `baja` → Badge neutral

---

### 5. Clientes
**Propósito:** CRUD de clientes con datos fiscales (RIF venezolano).

**Tabla:** ID · Nombre/Razón Social · RIF · Teléfono · Email · Ciudad · Máquinas (badge)

**Modal:** Nombre, RIF, Ciudad (grid 2), Teléfono, Email (grid 2)

---

### 6. Proveedores
**Propósito:** CRUD de proveedores.

**Tabla:** ID · Empresa · Contacto · Teléfono · Email · Ciudad · Productos (badge neutral)

**Modal:** Nombre empresa, Contacto+Ciudad (grid 2), Teléfono+Email (grid 2)

---

### 7. Reportes y Estadísticas
**Propósito:** Vista de KPIs y gráficos anuales.

**4 Stat Cards:** Servicios año, Máquinas gestionadas, Clientes activos, Valor inventario

**Gráfico de barras mensual** (SVG manual, 12 meses):
- Barras con label de valor encima
- Mes actual destacado con color sólido, resto con opacidad 60%
- Eje X: etiquetas de mes en 9px, color `#94A3B8`

**Gráfico de distribución** (barras de progreso horizontales):
- 4 categorías de servicio con barra de progreso proporcional

**Tabla Top Clientes:** Cliente · RIF · Máquinas · Servicios Totales · Último Servicio

---

### 8. Usuarios y Permisos
**Propósito:** Administración de cuentas y roles.

**3 Stat Cards:** Total / Activos / Roles

**Tabla:** # · Nombre · Email · Rol (badge) · Último Acceso · Estado (badge)

**Roles y colores:**
- Administrador → Badge purple
- Técnico → Badge default (azul)
- Recepcionista → Badge success (verde)

**Modal Nuevo Usuario:** Nombre, Email, Contraseña+Rol (grid 2)

---

## Componentes Reutilizables

### Sidebar
- Fondo `#1A2235`, ancho 230px (colapsado: 64px)
- Logo: cuadro 32×32px con color accent, border radius 8px, ícono printer blanco
- Nav items: 46px alto, gap 2px, border radius 8px, padding 10px 12px
- Estado activo: fondo accent, texto y ícono blancos
- Estado hover: `rgba(255,255,255,0.07)`
- Badge de alerta: fondo `#EF4444`, blanco, 10px, border radius pill
- Separador bottom: `rgba(255,255,255,0.07)`
- Botón Cerrar Sesión al fondo

### TopBar
- Altura 52px, fondo blanco, `border-bottom: 1px solid #E8EDF2`
- Botón hamburger (18px) + título del módulo actual (14px semibold)
- Flex-1 de espacio
- Ícono campana con dot rojo de notificación
- Avatar: círculo 30px con color accent, iniciales "AD" blancas 12px bold
- Info usuario: nombre (12px bold) + email (10px muted)

### Botón (Button)
| Variante | Fondo | Texto | Hover |
|---|---|---|---|
| primary | accent | blanco | accent-dark |
| secondary | `#F8FAFC` | `#334155` | `#EFF6FF` |
| success | `#16A34A` | blanco | `#15803D` |
| danger | `#DC2626` | blanco | `#C01E1E` |
| ghost | transparent | `#64748B` | `#F1F5F9` |
- Tamaño md: padding 8px 16px, font 13px
- Tamaño sm: padding 5px 12px, font 12px
- Border radius 8px, font-weight 600
- Transición: `all 0.15s`

### SearchBar
- Ícono lupa izquierda (padding-left 34px)
- Border `1.5px solid #E2E8F0`, border radius 8px, fondo blanco
- Placeholder color `#94A3B8`

### Tabla
- Header: 2px border-bottom, 11px uppercase, color `#64748B`, letter-spacing 0.05em
- Filas alternas: blanco / `#FAFBFC`
- Separador: `1px solid #F1F5F9`
- Padding celda: `10px 14px`
- Íconos de acción: ojo (gris), lápiz (accent), basura (rojo), 15px

### Modal
- Overlay: `rgba(15,23,42,0.45)`
- Contenedor: fondo blanco, border radius 14px, max-width 95vw, max-height 90vh
- Header: 18px 22px padding, border-bottom, título 16px bold, botón X
- Body: 22px padding
- Cierre al click fuera del contenedor

### Input / Select
- Border `1.5px solid #E2E8F0`, border radius 8px, padding 8px 12px
- Fondo `#F8FAFC`, font 13px, color `#0F172A`
- Focus: outline none (agregar ring en implementación)

### StatusSteps
- Círculo 28×28px, border radius 50%
- Completado: `#16A34A` + ícono check blanco
- Actual: accent
- Pendiente: `#E2E8F0`, texto `#94A3B8`
- Línea conectora: 2px, `#16A34A` si completada, `#E2E8F0` si pendiente
- Label: 10px debajo del círculo

---

## Interacciones y Comportamiento

### Navegación
- Click en ítem del sidebar → cambia módulo activo sin recarga
- Click en hamburger → colapsa/expande sidebar (animación 0.25s ease)
- Ícono bell → despliega panel de notificaciones (dropdown 300px)

### CRUD en todos los módulos
- Botón "Nuevo X" → abre modal con formulario vacío
- Ícono lápiz → abre modal con datos cargados
- Ícono basura → elimina inmediatamente del estado (sin confirmación en prototipo; en prod: dialog de confirmación)
- Ícono ojo → abre modal de detalle (solo lectura)

### Servicios — Kanban
- Click en tarjeta del kanban → abre modal de detalle
- Botón "Avanzar a [siguiente estado]" → incrementa `status` en 1 y cierra modal

### Búsqueda
- Filtrado en tiempo real al escribir (sin debounce en prototipo; recomendado en prod)

### Notificaciones
- Panel dropdown al click sobre campana
- Click fuera → no cierra (agregar en prod)

---

## Estado / State Management

Variables de estado principales por módulo:

```python
# Inventario
products: List[Product]  # lista de productos
search: str              # texto de búsqueda
modal_open: bool
edit_item: Product | None
form: dict

# Máquinas Fiscales
machines: List[Machine]
filter_status: str  # "all" | "activa" | "en_reparacion" | "dada_de_baja"
detail_open: bool
selected: Machine | None

# Servicios
services: List[Service]
# status: 0=Pendiente, 1=Asignada, 2=En Proceso, 3=Completada

# Global
active_module: str  # módulo activo
sidebar_collapsed: bool
accent_color: str
```

---

## Guía de Implementación en CustomTkinter

### Estructura recomendada
```
app/
├── main.py                  # Entry point, CTk App + main window
├── theme.py                 # Colores y tokens de diseño
├── components/
│   ├── sidebar.py           # CTkFrame sidebar con botones de nav
│   ├── topbar.py            # CTkFrame top bar
│   ├── stat_card.py         # CTkFrame tarjeta de estadística
│   ├── badge.py             # CTkLabel con estilo badge
│   ├── table.py             # CTkScrollableFrame con tabla custom
│   ├── modal.py             # CTkToplevel modal base
│   ├── button.py            # CTkButton con variantes de estilo
│   └── search_bar.py        # CTkEntry con ícono
├── modules/
│   ├── dashboard.py
│   ├── inventory.py
│   ├── fiscal_machines.py
│   ├── services.py
│   ├── clients.py
│   ├── suppliers.py
│   ├── reports.py
│   └── users.py
├── data/
│   ├── models.py            # Dataclasses / SQLAlchemy models
│   └── database.py          # SQLite connection
└── assets/
    └── icons/               # PNGs de íconos (CTkImage)
```

### Notas CustomTkinter
- Usar `CTkScrollableFrame` para las tablas y listas largas
- El sidebar usa `CTkFrame` con `CTkButton` (sin borde, fondo transparente, hover personalizado)
- Los modales son `CTkToplevel` centrados en la ventana principal
- Para los gráficos simples usar `matplotlib` embebido con `FigureCanvasTkAgg`, o `CTkCanvas` para barras SVG-style
- Los badges se implementan como `CTkLabel` con `corner_radius=20` y colores personalizados
- Fuente recomendada: `("Segoe UI", size, weight)` en Windows

---

## Archivos en este Paquete

| Archivo | Descripción |
|---|---|
| `Sistema de Gestion.html` | Prototipo principal — abrir en navegador para ver el diseño completo interactivo |
| `components.jsx` | Componentes React reutilizables (Icon, Badge, StatCard, Button, Table, Modal, etc.) |
| `tweaks-panel.jsx` | Panel de tweaks del prototipo (solo relevante para el HTML) |
| `README.md` | Este documento de handoff |

---

*Diseñado en Mayo 2026 · Color accent: `#e89754` · Estilo: Light mode, sidebar oscuro*
