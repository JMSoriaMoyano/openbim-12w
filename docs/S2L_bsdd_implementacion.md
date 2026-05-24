# bSDD — Implementación en el flujo NEXUM (Can Cabassa PBSA)

**Tipo:** Nota técnica complementaria a S2·L (BEP/EIR/plan de información)
**Autor:** Jose M. Soria
**Fecha:** 2026-05-18
**Versión:** 0.1
**Cuándo se aplica:** transversal · referenciado desde EIR §3 (clasificación), BEP §4.1.6 (Revit IFC config) y futuras S7·L–S9·L (IDS y CI/CD)

---

## 1. Qué es bSDD en una frase

bSDD (**buildingSMART Data Dictionary**) es un **servicio online gratuito** que aloja **diccionarios de clases y propiedades** estandarizadas para el entorno construido, con URIs persistentes, accesibles vía API REST/GraphQL ([buildingSMART · bSDD](https://www.buildingsmart.org/users/services/buildingsmart-data-dictionary/)).

En lenguaje práctico para NEXUM:

> bSDD es la **«fuente única de verdad»** para clasificaciones y nombres de propiedades. En lugar de escribir `"Wall_Exterior"` como string libre en Revit/IDS/IFC, escribimos un **URI bSDD** (`https://identifier.buildingsmart.org/uri/itec/gubimclass/.../EE-ME-MU-EX`) que cualquier software puede resolver para obtener: definición autoritativa, traducciones, propiedades asociadas, relaciones con otras clasificaciones, unidades, valores permitidos.

Implementa **ISO 12006-3** y **ISO 23386** sobre principios Linked Data ([bSDD overview](https://www.buildingsmart.org/users/services/buildingsmart-data-dictionary-old/)).

---

## 2. Por qué nos interesa en el flujo NEXUM

Sin bSDD, nuestro stack tiene 4 puntos débiles:

| # | Punto débil sin bSDD | Solución vía bSDD |
|---|---|---|
| 1 | EIR cita «clasificación GuBIMClass» como string. No hay validación automática. | El EIR cita el **URI del diccionario GuBIMClass** en bSDD. Cualquier IDS puede referenciar ese URI. |
| 2 | IDS define propiedades con nombres «a mano» (`FireRating`, `LoadBearing`). Riesgo de typos y de divergencia entre IDS. | IDS referencia el **URI bSDD de la propiedad** (`https://identifier.buildingsmart.org/uri/buildingsmart/ifc/4.3/prop/FireRating`). |
| 3 | Revit exporta clasificaciones como strings opacos. Imposible distinguir un código GuBIMClass de un código random. | Revit/Bonsai escriben **IfcClassificationReference con `Location` apuntando a bSDD**, trazable. |
| 4 | Cada disciplina puede usar sinónimos distintos para la misma propiedad (Resistencia al fuego / FireRating / RF). | Mapping centralizado: el `NEXUM_ParameterMapping.txt` traduce parámetros Revit ↔ propiedades bSDD. |

> **Resumen estratégico:** bSDD convierte nuestro IDS y nuestro EIR de «documentos con strings» en «documentos con identificadores resolubles». Es la condición previa para CI/CD real en S9·L.

---

## 3. Componentes del flujo NEXUM ↔ bSDD

Diagrama lógico (mental, sin ASCII art):

1. **EIR** (contrato cliente↔NEXUM) → declara qué clasificaciones y propiedades se exigen, **citando URIs bSDD**.
2. **BEP** (NEXUM↔equipo proyectista) → confirma cómo se materializa: setup Revit + mapping `.txt` + IDS.
3. **Revit IFC config** (`revit_ifc_export_config.json`) → habilita `ExportUserDefinedParameterMapping` y `ExportUserDefinedPsets`, que apuntan a `.txt` con códigos coherentes con bSDD.
4. **Modelo Revit (.rvt)** → en `Manage → Classification Settings` carga el diccionario GuBIMClass desde bSDD.
5. **IFC exportado** → contiene `IfcClassificationReference` con `Location` = URI bSDD.
6. **IDS NEXUM** (S7·L) → sus `<requirements>` referencian URIs bSDD vía `<classification dataType="IfcClassificationReference">` y `<property propertyset="..." baseName="...">` con URIs.
7. **ifctester / Validation Service** → valida el IFC contra el IDS resolviendo los URIs bSDD.
8. **CI/CD GitHub Actions** (S9·L) → ejecuta el paso 7 en cada PR.

---

## 4. Stack técnico de acceso a bSDD

### 4.1 Endpoints principales

| Recurso | URL | Uso |
|---|---|---|
| Web Search UI | https://search.bsdd.buildingsmart.org/ | Búsqueda humana de clases/propiedades. Útil para explorar antes de codificar. |
| REST API (Swagger) | https://app.swaggerhub.com/apis-docs/buildingSMART/Dictionaries/v1 | Documentación interactiva. |
| REST endpoint base | https://api.bsdd.buildingsmart.org | Llamadas programáticas REST. |
| GraphQL endpoint | https://api.bsdd.buildingsmart.org/graphqls | Consultas estructuradas complejas (POST). |
| URI resolver | https://identifier.buildingsmart.org/uri/{org}/{dictionary}/{version}/class/{code} | URI persistente que sirve HTML o JSON (header `Accept`). |

Documentación oficial integradores: [buildingSMART · Using the bSDD API](https://technical.buildingsmart.org/services/bsdd/using-the-bsdd-api/).

### 4.2 Métodos REST que usaremos en NEXUM

| Endpoint | Para qué | Quién lo llama en NEXUM |
|---|---|---|
| `GET /api/Dictionary/v1` | Listar diccionarios disponibles. | Onboarding inicial. |
| `GET /api/Dictionary/v1/Classes` | Listar clases de un diccionario (paginado). | Script de sincronización GuBIMClass↔IDS. |
| `GET /api/Class/v1?Uri={class_uri}` | Detalle de una clase (definición, traducciones, relaciones). | UI interna NEXUM y validación. |
| `GET /api/Class/Properties/v1?ClassUri={uri}` | Propiedades asociadas a una clase. | Generación automática de IDS facets. ([foro bSDD](https://forums.buildingsmart.org/t/bsdd-api-list-class-properties/6114)) |
| `GET /api/SearchList/v1` | Búsqueda textual cross-dictionary. | UI interna NEXUM. |
| `GET /api/Property/v1?Uri={prop_uri}` | Detalle de una propiedad (tipo de dato, unidad, valores permitidos). | Validador IDS. |

> **Autenticación:** los endpoints `GET` públicos no requieren auth para lectura. Para publicar diccionarios propios sí hace falta OAuth2 vía Azure B2C ([guía oficial](https://technical.buildingsmart.org/services/bsdd/using-the-bsdd-api/)).

### 4.3 Snippet Python base (cliente NEXUM)

Lo guardaremos en S4·L como `scripts/bsdd_client.py`:

```python
# scripts/bsdd_client.py (v0.1 — borrador conceptual S2·L)
"""Cliente minimal NEXUM para bSDD. Solo lectura, sin auth."""
import requests
from urllib.parse import quote

BSDD_BASE = "https://api.bsdd.buildingsmart.org/api"
HEADERS = {"Accept": "application/json"}

def get_class(class_uri: str) -> dict:
    """Devuelve detalle de una clase bSDD."""
    url = f"{BSDD_BASE}/Class/v1"
    r = requests.get(url, headers=HEADERS, params={"Uri": class_uri}, timeout=15)
    r.raise_for_status()
    return r.json()

def get_class_properties(class_uri: str) -> list[dict]:
    """Devuelve propiedades asociadas a una clase."""
    url = f"{BSDD_BASE}/Class/Properties/v1"
    r = requests.get(url, headers=HEADERS, params={"ClassUri": class_uri}, timeout=15)
    r.raise_for_status()
    return r.json().get("classProperties", [])

def search(text: str, dictionary_uri: str | None = None, limit: int = 25) -> list[dict]:
    """Búsqueda textual; opcionalmente filtrada a un diccionario."""
    url = f"{BSDD_BASE}/SearchList/v1"
    params = {"SearchText": text, "Limit": limit}
    if dictionary_uri:
        params["DictionaryUris"] = dictionary_uri
    r = requests.get(url, headers=HEADERS, params=params, timeout=15)
    r.raise_for_status()
    return r.json().get("classes", [])

if __name__ == "__main__":
    # Ejemplo: IfcWall canónico
    uri = "https://identifier.buildingsmart.org/uri/buildingsmart/ifc/4.3/class/IfcWall"
    cls = get_class(uri)
    print(f"Nombre: {cls.get('name')}")
    print(f"Definición: {cls.get('definition', '')[:200]}")
    props = get_class_properties(uri)
    print(f"\n{len(props)} propiedades asociadas. Primeras 5:")
    for p in props[:5]:
        print(f"  - {p.get('name')} ({p.get('propertyUri', '')})")
```

> Este script se ejecuta en seco y prueba la conectividad bSDD. Será la base de las facets generadas automáticamente en S7·L.

---

## 5. Diccionarios relevantes para Can Cabassa

| Diccionario | URI base | Uso NEXUM |
|---|---|---|
| **IFC 4.3** (canónico buildingSMART) | `https://identifier.buildingsmart.org/uri/buildingsmart/ifc/4.3/` | Entidades base (IfcWall, IfcSpace…) y Pset_Common. |
| **GuBIMClass** (ITeC, Catalunya) | publicado por ITeC (verificar URI exacto en bSDD Search) | Clasificación obligatoria por EIR §3, contractual con cliente. |
| **CTE-DB-SI** (no oficial; candidato a publicar) | n/a hoy | Propiedades de seguridad en caso de incendio según CTE. NEXUM podría publicar un dominio propio en bSDD si es estratégico. |
| **BREEAM ES** (no oficial) | n/a hoy | Ídem ESG. |

**Acción S3·L:** confirmar en https://search.bsdd.buildingsmart.org/ el URI exacto del dominio GuBIMClass publicado por ITeC, fijarlo en EIR §3.1 y BEP §4.1.6.

---

## 6. Integración por software del stack NEXUM

### 6.1 Revit (productivo, equipos ARQ/MEP/EST)

**Vía 1 — Plugin oficial bSDD (recomendado para 2026):**
- Plugin gratuito de VolkerVessels/Heijmans listado en [bSDD software](https://www.buildingsmart.org/users/services/buildingsmart-data-dictionary/).
- Permite al modelador buscar clases bSDD desde un panel y aplicarlas a elementos.
- Las clasificaciones se guardan en `IfcClassificationReference` al exportar a IFC.

**Vía 2 — Classification Settings nativo de Revit:**
- `Manage → Classification → Add` apuntando al fichero descargado de bSDD (CSV o JSON).
- Limitación: snapshot offline. Requiere disciplina de refresco trimestral.
- Es el camino documentado en `revit_ifc_export_config.json` línea 57: `notes_no_guardados_en_json` incluye `"Classification Settings (Name: GuBIMClass; debe configurarse en el modelo y sincronizarse)"`.

**Decisión NEXUM:**
- **H1 Anteproyecto y H2 Básico:** Vía 2 (snapshot offline) por simplicidad.
- **H3 Ejecutivo y H4 As-built:** evaluar Vía 1 (plugin live) si el volumen de clasificaciones a aplicar > 200 elementos.

### 6.2 Bonsai (Blender) — uso para QA y exploración

Bonsai (anteriormente BlenderBIM) **soporta bSDD nativamente** ([Bonsai docs](https://docs.ifcopenshell.org/bonsai.html), [tutorial Bonsai+bSDD](https://www.youtube.com/watch?v=Eqtqun9JrWM)):

1. Abrir Blender + Bonsai.
2. Panel BIM → `Classification` → cargar diccionario GuBIMClass desde bSDD (con conexión a internet, sin descarga manual).
3. Asignar clasificaciones a elementos del IFC importado.
4. Re-exportar IFC con clasificaciones embebidas.

Caso de uso NEXUM: **enriquecer IFCs heredados de subcontratistas** que entreguen IFC sin clasificaciones, antes de meterlos al CDE. Se documentará como procedimiento en S5·L (autoría IfcOpenShell).

> Issue conocido: Bonsai aún no permite asignar Psets **no IFC** desde bSDD ([IfcOpenShell #5404](https://github.com/IfcOpenShell/IfcOpenShell/issues/5404)). No bloqueante: nuestros Psets propios `Pset_NEXUM_*` los gestionamos vía `UserDefinedPsets.txt` en Revit.

### 6.3 IDS (Information Delivery Specification) — la clave del rigor

Un IDS sin bSDD declara cosas como:

```xml
<property dataType="IfcReal">
  <propertySet><simpleValue>Pset_WallCommon</simpleValue></propertySet>
  <baseName><simpleValue>FireRating</simpleValue></baseName>
</property>
```

Funciona, pero el `FireRating` es un string suelto. Con bSDD podemos elevarlo:

```xml
<property dataType="IfcLabel" uri="https://identifier.buildingsmart.org/uri/buildingsmart/ifc/4.3/prop/FireRating">
  <propertySet><simpleValue>Pset_WallCommon</simpleValue></propertySet>
  <baseName><simpleValue>FireRating</simpleValue></baseName>
</property>
```

Y para clasificaciones, el facet `Classification` referencia bSDD directamente:

```xml
<classification uri="https://identifier.buildingsmart.org/uri/itec/gubimclass/.../EE-ME-MU-EX">
  <value><simpleValue>EE-ME-MU-EX</simpleValue></value>
  <system><simpleValue>GuBIMClass</simpleValue></system>
</classification>
```

> **Lo veremos a fondo en S7·L–S8·L.** Aquí solo introducimos la sintaxis para que el concepto esté presente al cerrar S2·L.

Revisión de literatura de respaldo: [«Application of IDS Standard and bSDD in BIM Workflows: A Systematic Literature Review» (EC-3 2025)](https://ec-3.org/publications/conference/paper/?id=EC32025_273).

### 6.4 Plannerly — alternativa de IDS authoring asistida

[Plannerly](https://plannerly.com/) ofrece un editor visual de IDS que **lee directamente de bSDD** ([demo oficial](https://www.youtube.com/watch?v=Zz0PZNkMKXM)). Útil si en algún momento NEXUM externaliza la redacción de IDS a un consultor sin perfil de programador.

Posicionamiento NEXUM: editar el IDS en XML directamente (control total, diff en Git). Plannerly queda como **alternativa de revisión visual** con el cliente.

---

## 7. Plan de implementación bSDD por sesiones

| Sesión | Fecha | Acción bSDD |
|---|---|---|
| **S2·L** (hoy) | 18/05 | Documento conceptual (este fichero). Cita bSDD en EIR §3 y BEP §4.1.6 — pendiente. |
| **S2·X** | 20/05 | Mención bSDD en lectura comentada del JSON: `ExportUserDefinedParameterMapping.txt` debe alinearse con propiedades bSDD. |
| **S3·L** | 25/05 | Confirmar URI de GuBIMClass en bSDD Search. Anotar URI en EIR §3.1 y BEP §4.1.6. |
| **S4·L** | 01/06 | Implementar `scripts/bsdd_client.py` v0.2 con tests pytest. |
| **S5·L** | 08/06 | Demo IfcOpenShell: leer `IfcClassificationReference` de un IFC y resolver URI bSDD. |
| **S6·L** | 15/06 | Añadir al pipeline de calidad un paso `bsdd_resolve.py` que valide que todos los `IfcClassificationReference.Location` resuelven a clases vivas en bSDD. |
| **S7·L** | 22/06 | IDS NEXUM con `uri` apuntando a propiedades bSDD. |
| **S8·L** | 29/06 | ifctester + IDS + bSDD: validación end-to-end. |
| **S9·L** | 06/07 | GitHub Action que ejecuta el resolver bSDD en CI. Caching de respuestas para no machacar la API. |
| **S11·L** | 20/07 | Speckle CDE: configurar webhooks para revalidar bSDD al recibir nuevo IFC. |

---

## 8. Antipatrones y riesgos

**A1 — Copy-paste de URIs sin verificar resolución.**
Si el URI cambia de versión (ej. paso de IFC 4.3 a IFC 5.0), el IDS apunta a un recurso inexistente. Mitigación: el `bsdd_client.py` resuelve cada URI antes de aceptar un IDS.

**A2 — Usar IDs internos en lugar de URIs.**
bSDD distingue entre `Code` (humano, p.ej. `EE-ME-MU-EX`) y `Uri` (técnico, único, persistente). Los IDS deben referenciar **siempre el `Uri`**. El `Code` solo aparece en el `<value>`.

**A3 — Asumir que GuBIMClass = OmniClass = Uniclass.**
Cada diccionario tiene su lógica jerárquica. No se pueden mapear 1:1 sin perder semántica. Si el cliente exige Uniclass y NEXUM aplica GuBIMClass, hay que **declararlo explícitamente** en EIR §3 y proveer **doble clasificación** (el IFC admite múltiples `IfcClassificationReference` por elemento).

**A4 — Confiar en clasificación de subcontratistas sin auditar.**
Recibir un IFC con `IfcClassificationReference` no garantiza que el `Location` resuelva a un URI bSDD válido. Por eso S6·L incluye el resolver: cada entrega externa pasa por validación bSDD antes de ingresar al CDE.

**A5 — Confundir IFC dictionary con dictionaries de terceros.**
El propio IFC tiene su dictionary publicado en bSDD, pero **no contiene todas las entidades IFC** ([nota técnica](https://technical.buildingsmart.org/services/bsdd/using-the-bsdd-api/)). Si se busca `IfcAlignmentHorizontalSegment`, la API devolverá vacío porque no está registrado. Mitigación: cubrir esos gaps usando IDS facets `Entity` sin URI (más permisivos).

---

## 9. Decisiones para validar contigo antes de S3·L

1. **¿Publica NEXUM su propio dominio bSDD `nexum.developments`?** Sería el contenedor para `Pset_NEXUM_*` y clasificaciones internas (tipologías PBSA, niveles de acabado). Pros: trazabilidad total, posicionamiento sectorial. Contras: requiere mantenimiento (governance, versionado), OAuth setup.
2. **¿Doble clasificación o solo GuBIMClass?** EIR actual cita solo GuBIMClass. Si forward-funding internacional, ¿añadimos Uniclass para inversores UK/IE?
3. **¿Plugin bSDD en Revit desde H1 o desde H3?** Coste de aprendizaje vs ganancia de productividad.
4. **¿Cacheo local de bSDD o llamadas live?** Para CI/CD masivo conviene cache local (snapshot diario). Para QA puntual basta con calls live.

---

## 10. Referencias

- [buildingSMART · bSDD overview](https://www.buildingsmart.org/users/services/buildingsmart-data-dictionary/)
- [buildingSMART Technical · Using the bSDD API](https://technical.buildingsmart.org/services/bsdd/using-the-bsdd-api/)
- [Swagger · bSDD Dictionaries API v1](https://app.swaggerhub.com/apis-docs/buildingSMART/Dictionaries/v1)
- [bSDD Search UI](https://search.bsdd.buildingsmart.org/)
- [Foro bSDD · List class properties](https://forums.buildingsmart.org/t/bsdd-api-list-class-properties/6114)
- [Bonsai · bSDD classification tutorial](https://www.youtube.com/watch?v=Eqtqun9JrWM)
- [IfcOpenShell docs · Bonsai](https://docs.ifcopenshell.org/bonsai.html)
- [EC-3 2025 · IDS + bSDD systematic review](https://ec-3.org/publications/conference/paper/?id=EC32025_273)
- [Plannerly · IDS + bSDD demo](https://www.youtube.com/watch?v=Zz0PZNkMKXM)
- [GuBIMClass · ITeC](https://www.gubimclass.org/)

---

## Document Revision History

| Versión | Fecha | Autor | Cambios |
|---|---|---|---|
| 0.1 | 2026-05-18 | Jose M. Soria | Versión inicial · concepto + stack técnico + plan por sesiones + antipatrones + decisiones pendientes |
