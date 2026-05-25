# models/samples — Manifest de IFCs de referencia

**Documento:** `SOURCES.md`
**Versión:** 1.0
**Fecha:** 25/05/2026
**Sesión origen:** S3·L (semana 3, lunes) — IFC schema: jerarquía y relaciones
**Mantenedor:** José M. Soria (`jmsoria@ciccp.es`)
**Política de versionado:** Opción B del plan formativo 12w. Los binarios `.ifc` **no se versionan en git**. Este documento es el manifest canónico que define qué IFC se usa, dónde se obtiene y cómo verificar su integridad.

---

## 1. Política de la carpeta

| Subcarpeta | Estado git | Propósito |
|---|---|---|
| `models/samples/` | versionado | Carpeta padre, contiene este `SOURCES.md` y `.gitkeep` |
| `models/samples/_local/` | **ignorado** (`.gitignore` línea 41) | IFCs descargados por cada desarrollador en su máquina |

**Regla:** ningún `.ifc` entra en git. Si se necesita versionar un IFC pequeño (≤200 KB) generado en el proyecto, ir a `models/` raíz o crear `models/generated/` con política explícita.

**Migración futura:** cuando el catálogo supere 5 IFCs o se necesite trazabilidad fuerte (revisión cruzada de modelos), migrar a **Git LFS** (planificado para S5·L o cuando aplique).

---

## 2. Catálogo de IFCs de referencia

### 2.1 · AC20-FZK-Haus

Modelo didáctico de referencia para todo el plan formativo. Vivienda unifamiliar simple (Phantasy Building) producida por KIT/IAI como ejemplo público de IFC4.

| Campo | Valor |
|---|---|
| **Identificador interno** | `FZK_HAUS_IFC4` |
| **Nombre fichero** | `AC20-FZK-Haus.ifc` |
| **Schema declarado** | `IFC4` (línea `FILE_SCHEMA(('IFC4'))` del HEADER) |
| **Tamaño** | 2 570 803 bytes (2,45 MB) |
| **SHA-256** | `70cc8ff245fc0894201d96496c031005a5cbd7a96b22d8a1b87c5a883fb77994` |
| **MVD declarado** | ViewDefinition (Coordination View + QuantityTakeOffAddOnView + SpaceBoundary2ndLevelAddOnView) |
| **Originating system** | GRAPHISOFT ARCHICAD-64 20.0.0 GER FULL (IFC2x3 add-on 4009, reexportado a IFC4) |
| **Fecha del modelo** | 21/12/2016 17:54:06 |
| **Ruta local esperada** | `models/samples/_local/AC20-FZK-Haus.ifc` |

#### Fuente primaria (canónica)

- **URL directa:** https://www.ifcwiki.org/images/e/e3/AC20-FZK-Haus.ifc
- **Página de descripción:** https://www.ifcwiki.org/index.php?title=File:AC20-FZK-Haus.ifc
- **Catálogo:** https://www.ifcwiki.org/index.php?title=KIT_IFC_Examples
- **Last-Modified upstream:** 15/11/2021

#### Fuente alternativa (mirror)

- **URL:** https://www.steptools.com/docs/stpfiles/ifc/AC20-FZK-Haus.ifc
- **Nota:** versión más antigua (31/07/2021), tamaño 2 526 544 bytes. **No usar como primaria.** Solo como respaldo si la fuente KIT está caída.

#### Autoría y licencia

> Institute for Automation and Applied Informatics (IAI) — Karlsruhe Institute of Technology (KIT).
> Uso sin restricciones para fines académicos, formativos y de desarrollo.
> En publicaciones citar: *Institute for Automation and Applied Informatics (IAI) / Karlsruhe Institute of Technology (KIT)*.

---

## 3. Procedimiento de descarga (reproducible)

### 3.1 · Windows (recomendado: PowerShell)

Desde la raíz del repo `openbim-12w\`:

```cmd
powershell -Command "Invoke-WebRequest -Uri 'https://www.ifcwiki.org/images/e/e3/AC20-FZK-Haus.ifc' -OutFile 'models\samples\_local\AC20-FZK-Haus.ifc'"
```

### 3.2 · macOS / Linux

```bash
mkdir -p models/samples/_local
curl -L -o models/samples/_local/AC20-FZK-Haus.ifc "https://www.ifcwiki.org/images/e/e3/AC20-FZK-Haus.ifc"
```

### 3.3 · Notas sobre TLS en Windows

`curl` de Windows (Schannel) puede fallar con `CRYPT_E_NO_REVOCATION_CHECK (0x80092012)` por la política estricta de verificación de revocación. Alternativas:
- Usar **PowerShell con `Invoke-WebRequest`** (recomendado).
- Usar `curl --ssl-no-revoke ...` (salta la verificación de revocación, mantiene la del certificado).

---

## 4. Verificación de integridad (obligatoria)

Después de cada descarga, verificar el SHA-256 antes de usar el fichero en cualquier ejercicio.

### 4.1 · Windows

```cmd
certutil -hashfile models\samples\_local\AC20-FZK-Haus.ifc SHA256
```

### 4.2 · macOS / Linux

```bash
sha256sum models/samples/_local/AC20-FZK-Haus.ifc
```

### 4.3 · Valor esperado

```
70cc8ff245fc0894201d96496c031005a5cbd7a96b22d8a1b87c5a883fb77994
```

Si el hash **no coincide**: borrar el fichero, no usarlo en ningún script ni ejercicio, repetir la descarga. Si tras 3 intentos sigue sin coincidir, comprobar manualmente con visor (KITModelViewer / FZKViewer) y reportar incidencia.

---

## 5. Uso en scripts y ejercicios

### 5.1 · Convención de ruta

Los scripts del repo deben referenciar el IFC con ruta relativa desde la raíz del repo:

```python
IFC_PATH = "models/samples/_local/AC20-FZK-Haus.ifc"
```

### 5.2 · Comprobación previa en scripts

Todo script que consuma este IFC debe comprobar al inicio:

```python
import hashlib
from pathlib import Path

IFC_PATH = Path("models/samples/_local/AC20-FZK-Haus.ifc")
EXPECTED_SHA256 = "70cc8ff245fc0894201d96496c031005a5cbd7a96b22d8a1b87c5a883fb77994"

if not IFC_PATH.exists():
    raise FileNotFoundError(
        f"Falta {IFC_PATH}. Descárgalo siguiendo models/samples/SOURCES.md §3."
    )

actual = hashlib.sha256(IFC_PATH.read_bytes()).hexdigest()
if actual != EXPECTED_SHA256:
    raise ValueError(
        f"SHA-256 no coincide. Esperado {EXPECTED_SHA256}, obtenido {actual}. "
        "Repite descarga desde models/samples/SOURCES.md §3."
    )
```

---

## 6. Trazabilidad

| Acción | Fecha | Commit/sesión | Notas |
|---|---|---|---|
| Manifest creado | 25/05/2026 | S3·L | Versión 1.0, IFC único: AC20-FZK-Haus |
| Próxima revisión prevista | S5·L (junio 2026) | — | Evaluar añadir 1–2 IFCs más (infraestructura, multidisciplinar) |
| Migración a Git LFS | a decidir | S5–S6 | Si el catálogo crece >5 IFCs o se versiona algún binario |
