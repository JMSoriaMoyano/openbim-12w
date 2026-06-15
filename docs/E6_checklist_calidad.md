# E6 · Checklist de calidad BIM (aplicación FZK-Haus)

**Fecha redacción:** 15/06/2026 (S6·L)
**Fecha cierre prevista:** 20/06/2026 (S6·S · tag `e6-closed`)
**Modelo objeto:** `AC20-FZK-Haus.ifc` (modelo autoriado: `out/AC20-FZK-Haus_authored.ifc`)
**EIR de referencia:** PBSA v0.2 (4 variantes vigentes)
**Marco normativo interno:** `docs/S6L_marco_calidad.md` v1.0
**Autor:** José M. Soria · NEXUM Developments
**Versión documento:** 1.0

---

## 1. Objeto

Este documento materializa el marco de calidad de `S6L_marco_calidad.md` en una **checklist accionable** que se ejecutará sobre el modelo FZK-Haus autoriado a lo largo de la semana S6 (15/06 – 20/06). Define qué chequeos componen el entregable E6, qué evidencias se aceptan y qué criterio de cierre permite aplicar el tag `e6-closed`.

### 1.1 Alcance

- Aplica a las 4 variantes EIR v0.2: común, diseño, contratista, asbuilt.
- Aplica al modelo `out/AC20-FZK-Haus_authored.ifc` (heredado de S5·L autoría) como modelo de referencia reproducible.
- Cubre las 8 dimensiones del marco de calidad, ordenadas por capa ISO 19650-2.

### 1.2 No-objetivos

- No sustituye el motor de calidad refactorizado `quality_engine/` (Bloque D · estructura) ni el prototipo IDS XML (Bloque E). E6 valida que el marco se aplica correctamente al modelo, no que la implementación del motor sea final.
- No introduce nuevos modelos: FZK-Haus es el único modelo del entregable E6.
- No define thresholds ad-hoc por checks individuales: hereda los thresholds genéricos del marco §5.1.

---

## 2. Tabla resumen · 28 checks E6 sobre FZK-Haus

| ID | Dimensión | Capa ISO | Variantes aplicables | Criterio | Backend target |
|---|---|---|---|---|---|
| **C-M-01** | D1 Modelo | No gráfica | todas | `FILE_SCHEMA == 'IFC4'` | Motor propio |
| **C-M-02** | D1 Modelo | No gráfica | todas | `model.schema == 'IFC4'` (coherencia) | Motor propio |
| **C-M-03** | D1 Modelo | No gráfica | todas | `nº IfcProject == 1` | IDS (`minOccurs/maxOccurs`) |
| **C-M-04** | D1 Modelo | No gráfica | todas | `nº IfcSite ≥ 1` | IDS |
| **C-M-05** | D1 Modelo | No gráfica | todas | `nº IfcBuilding ≥ 1` | IDS |
| **C-M-06** | D1 Modelo | No gráfica | todas | `nº IfcBuildingStorey ≥ 1` | IDS |
| **C-P-01** | D2 Propiedades | No gráfica | todas | 100% muros con `Pset_WallCommon` | IDS |
| **C-P-02** | D2 Propiedades | No gráfica | todas | 100% puertas con `Pset_DoorCommon` | IDS |
| **C-P-03** | D2 Propiedades | No gráfica | todas | 100% puertas con `FireRating` definido | IDS |
| **C-P-04** | D2 Propiedades | No gráfica | todas | 100% muros con `IsExternal` definido | IDS |
| **C-P-05** | D2 Propiedades | No gráfica | todas | 100% muros con `LoadBearing` definido | IDS |
| **C-R-01** | D3 Relaciones | No gráfica | todas | 100% productos físicos con containment a `IfcBuildingStorey` | Motor propio |
| **C-R-02** | D3 Relaciones | No gráfica | todas | jerarquía Project→Site→Building→Storey completa | Motor propio |
| **C-R-03** | D3 Relaciones | No gráfica | todas | nº elementos huérfanos == 0 | Motor propio |
| **C-G-01** | D4 Geometría | Gráfica | todas | 100% productos físicos con `IfcProductDefinitionShape` | IDS |
| **C-G-02** | D4 Geometría | Gráfica | todas | 100% productos físicos con bounding box no nulo | Motor propio |
| **C-G-03** | D4 Geometría | Gráfica | todas | muros con representación `Body` y `Axis` coherentes | Motor propio |
| **C-U-01** | D5 Unidades | No gráfica | todas | `IfcUnitAssignment` presente | Motor propio |
| **C-U-02** | D5 Unidades | No gráfica | todas | sistema métrico SI (m, m², m³, °) | Motor propio |
| **C-U-03** | D5 Unidades | No gráfica | todas | sniff test longitudes coherente | Motor propio (sniff) |
| **C-C-01** | D6 Clasificación | No gráfica | todas | ≥ 1 sistema de clasificación declarado | IDS |
| **C-C-02** | D6 Clasificación | No gráfica | todas | ≥ 70% muros con código de clasificación | IDS |
| **C-T-01** | D7 Temporal | No gráfica | contratista · asbuilt | ≥ 1 `IfcTask` declarada | IDS |
| **C-T-02** | D7 Temporal | No gráfica | contratista | ≥ 80% productos con tarea asignada | IDS |
| **C-T-03** | D7 Temporal | No gráfica | asbuilt | ≥ 1 hito as-built declarado | IDS |
| **C-Q-01** | D8 Coste | No gráfica | diseño | 100% muros con `Qto_WallBaseQuantities` | IDS |
| **C-Q-02** | D8 Coste | No gráfica | diseño | ≥ 80% productos con `IfcCostItem` asociado | IDS |
| **C-Q-03** | D8 Coste | No gráfica | diseño | sniff QTO coherente (cantidad declarada vs calculada) | Motor propio (sniff) |

**Resumen de aplicabilidad por variante:**

| Variante | Checks aplicables | Distribución backend |
|---|---|---|
| común | 22 (C-M-* · C-P-* · C-R-* · C-G-* · C-U-* · C-C-*) | 13 IDS · 9 motor propio |
| diseño | 22 + 3 (C-Q-*) = **25** | 14 IDS · 11 motor propio |
| contratista | 22 + 2 (C-T-01, C-T-02) = **24** | 15 IDS · 9 motor propio |
| asbuilt | 22 + 2 (C-T-01, C-T-03) = **24** | 15 IDS · 9 motor propio |

**Distribución global checks:** 28 únicos · **18 migrables a IDS (64%)** · **10 quedan en motor propio (36%)** — coherente con la previsión §4.2 del marco (~70% migrable).

---

## 3. Detalle por dimensión

### 3.1 · D1 Modelo (C-M-01 a C-M-06)

**Qué se valida:** integridad estructural mínima del IFC.

**Checks:**

- **C-M-01** · `FILE_SCHEMA == 'IFC4'` — verificar la línea STEP `FILE_SCHEMA(('IFC4'));`. Crítico: FZK-Haus es IFC4 confirmado tras DT-S5L-01.
- **C-M-02** · `model.schema == 'IFC4'` — coherencia entre cabecera STEP y schema cargado por ifcopenshell. La lección DT-S5L-01 nos enseñó que `FILE_NAME.originating_system` no es fuente de verdad.
- **C-M-03** · `nº IfcProject == 1` — exactamente un IfcProject (no menos, no más).
- **C-M-04** · `nº IfcSite ≥ 1` — al menos un site.
- **C-M-05** · `nº IfcBuilding ≥ 1` — al menos un building.
- **C-M-06** · `nº IfcBuildingStorey ≥ 1` — al menos una planta.

**Evidencias esperadas en E6:**
- Salida `model.schema` capturada en log (texto).
- Conteos de entidades raíz exportados en JSON (`out/<modelo>_compliance_post_<variante>.json`).

**Estado previsto FZK-Haus:** todos en `pass` (modelo verificado en S4·S y S5·L).

### 3.2 · D2 Propiedades (C-P-01 a C-P-05)

**Qué se valida:** Psets obligatorios y propiedades específicas críticas.

**Checks:**

- **C-P-01** · 100% muros con `Pset_WallCommon` — obligatorio en IFC4.
- **C-P-02** · 100% puertas con `Pset_DoorCommon`.
- **C-P-03** · 100% puertas con `FireRating` definido — el check estrella mejorado por la autoría S5·L (40% → 100% en H3.DOOR.FireRating).
- **C-P-04** · 100% muros con `IsExternal` definido — distinción muro exterior vs interior, crítica para simulación energética.
- **C-P-05** · 100% muros con `LoadBearing` definido — distinción estructural vs partición, crítica para integración con cálculo.

**Evidencias esperadas en E6:**
- Matriz `out/AC20-FZK-Haus_compliance_post_<variante>.json` con bloque `properties_checks[]`.
- Tabla en `out/AC20-FZK-Haus_audit_report_<variante>.md` con % completitud por check.

**Estado previsto FZK-Haus:** C-P-01, C-P-02, C-P-03 en `pass`; C-P-04, C-P-05 en `partial` o `fail` (no verificados específicamente en E4/E5).

### 3.3 · D3 Relaciones (C-R-01 a C-R-03)

**Qué se valida:** lógica espacial y constructiva del modelo.

**Checks:**

- **C-R-01** · 100% productos físicos con containment a `IfcBuildingStorey` vía `IfcRelContainedInSpatialStructure`. El muro autoriado en S5·L (GlobalId `3sSuArjhP1VAHDFwRlK_Hf`) es trazable aquí.
- **C-R-02** · jerarquía Project→Site→Building→Storey completa vía `IfcRelAggregates`.
- **C-R-03** · nº elementos huérfanos == 0 (sin containment ni agregación).

**Evidencias esperadas en E6:**
- JSON con conteos `productos_con_containment / productos_total`.
- Lista de elementos huérfanos si los hay (con GlobalId).

**Estado previsto FZK-Haus:** todos en `pass`.

### 3.4 · D4 Geometría (C-G-01 a C-G-03)

**Qué se valida:** validez geométrica representable.

**Checks:**

- **C-G-01** · 100% productos físicos con `IfcProductDefinitionShape`. Después de las 7 entidades de la operación de autoría S5·L, esto debe estar al 100%.
- **C-G-02** · 100% productos físicos con bounding box calculable y no nulo.
- **C-G-03** · muros con representación `Body` (sólido) y `Axis` (línea de eje) coherentes — distancia eje al centroide del sólido < tolerancia.

**Evidencias esperadas en E6:**
- JSON con conteos.
- Captura PNG opcional del modelo abierto en Bonsai (verificación visual del muro autoriado).

**Estado previsto FZK-Haus:** C-G-01, C-G-02 en `pass`; C-G-03 a verificar (el muro autoriado podría no tener `Axis`).

### 3.5 · D5 Unidades (C-U-01 a C-U-03)

**Qué se valida:** sistema de unidades coherente.

**Checks:**

- **C-U-01** · `IfcUnitAssignment` presente y referenciado por `IfcProject`.
- **C-U-02** · sistema métrico SI: longitud en metros, superficie en m², volumen en m³, ángulo en grados (o radianes si se declara explícitamente).
- **C-U-03** · sniff test longitudes: muestreo aleatorio de 10 longitudes de muro; si la mediana es > 100, probable que las unidades reales sean milímetros aunque se declare metro.

**Evidencias esperadas en E6:**
- JSON con declaración `IfcUnitAssignment` extraída.
- Salida del sniff test (lista de longitudes muestreadas).

**Estado previsto FZK-Haus:** todos en `pass` (FZK-Haus es modelo métrico SI canónico).

### 3.6 · D6 Clasificación (C-C-01 a C-C-02)

**Qué se valida:** asignación de clasificación externa.

**Checks:**

- **C-C-01** · ≥ 1 sistema de clasificación declarado vía `IfcClassification`.
- **C-C-02** · ≥ 70% muros con `IfcRelAssociatesClassification` a un código de clasificación.

**Evidencias esperadas en E6:**
- JSON con sistemas declarados (`name`, `source`, `edition`).
- % muros clasificados.

**Estado previsto FZK-Haus:** **probable `fail`** en ambos. FZK-Haus es modelo de muestra sin clasificación. Este es uno de los checks que demuestra que el marco detecta gaps reales del modelo, no solo los pasa todos.

### 3.7 · D7 Temporal · 4D (C-T-01 a C-T-03)

**Aplica:** contratista (C-T-01, C-T-02) · asbuilt (C-T-01, C-T-03).

**Qué se valida:** planificación y secuenciación.

**Checks:**

- **C-T-01** · ≥ 1 `IfcTask` declarada en el modelo.
- **C-T-02** · ≥ 80% productos con tarea asignada vía `IfcRelAssignsToProcess` (variante contratista).
- **C-T-03** · ≥ 1 hito as-built declarado vía `IfcTask` con `TaskType == 'COMPLETION'` (variante asbuilt).

**Evidencias esperadas en E6:**
- JSON con conteos de tareas y asignaciones.

**Estado previsto FZK-Haus:** `fail` en las 3 (modelo sin 4D). Esperado y documentado como gap formativo: estos checks son aspiracionales hasta introducir modelo PBSA propio.

### 3.8 · D8 Coste · 5D (C-Q-01 a C-Q-03)

**Aplica:** diseño exclusivamente.

**Qué se valida:** mediciones y control de coste.

**Checks:**

- **C-Q-01** · 100% muros con `Qto_WallBaseQuantities`.
- **C-Q-02** · ≥ 80% productos con `IfcCostItem` asociado vía `IfcRelAssignsToControl`.
- **C-Q-03** · sniff QTO: comparar `Qto_WallBaseQuantities.NetVolume` declarado vs volumen calculable desde geometría. Tolerancia 5%.

**Evidencias esperadas en E6:**
- JSON con presencia/ausencia de Qto por elemento.
- Tabla sniff QTO (declarado vs calculado vs delta).

**Estado previsto FZK-Haus:** `fail` en C-Q-02, posible `partial` en C-Q-01 y C-Q-03 (FZK-Haus tiene algunos `Qto_*` parciales).

---

## 4. Criterios de aceptación E6 · cierre sábado 20/06

Para aplicar el tag `e6-closed` deben cumplirse **todos** los siguientes criterios:

| # | Criterio | Estado al firmar E6 |
|---|---|---|
| 1 | `docs/S6L_marco_calidad.md` v1.0 firmado | ✅ (este lunes) |
| 2 | `docs/E6_checklist_calidad.md` v1.0 firmado | ✅ (este lunes) |
| 3 | `quality_engine/` estructura modular creada (Bloque D, no implementación completa) | ⏳ hoy |
| 4 | `ids/PBSA_v0.2_prototype.ids` con ≥ 2 reglas IDS válidas (validables con `ifctester`) | ⏳ hoy |
| 5 | `out/AC20-FZK-Haus_compliance_post_<variante>.json` regenerados con marco v1.0 para las 4 variantes | ⏳ S6·X (Mié 17/06) |
| 6 | `out/AC20-FZK-Haus_audit_report_<variante>.md` (resumen humano) generado para las 4 variantes | ⏳ S6·X |
| 7 | `out/AC20-FZK-Haus_compliance_ids_*.json` con resultado del backend IDS sobre el prototipo (≥ 1 variante) | ⏳ S6·X |
| 8 | `docs/E6_auditoria_calidad_fzk_haus.md` v1.0 redactado (entregable síntesis E6) | ⏳ S6·S (Sáb 20/06) |
| 9 | `docs/S6L_notas_sesion.md`, `S6X_notas_sesion.md`, `S6S_notas_sesion.md` redactados | ⏳ progresivo |
| 10 | Tag `e6-closed` sobre commit final | ⏳ S6·S |

**Estado al cierre S6·L (esta sesión):** 2 de 10 criterios verdes. Resto progresivo S6·X y S6·S.

---

## 5. Formato de evidencias E6

Según convención §6 del marco:

```
out/
├── AC20-FZK-Haus_compliance_post_comun.json        ← matriz motor propio (regenerado v1.0)
├── AC20-FZK-Haus_compliance_post_diseno.json
├── AC20-FZK-Haus_compliance_post_contratista.json
├── AC20-FZK-Haus_compliance_post_asbuilt.json
├── AC20-FZK-Haus_compliance_ids_comun.json         ← matriz backend IDS (≥ 1 variante)
├── AC20-FZK-Haus_audit_report_comun.md             ← resumen humano
├── AC20-FZK-Haus_audit_report_diseno.md
├── AC20-FZK-Haus_audit_report_contratista.md
└── AC20-FZK-Haus_audit_report_asbuilt.md
```

Los reports `.md` siguen plantilla simple: portada (modelo + variante + EIR) + tabla 28 checks con estado + sección de hallazgos + footer (timestamp + SHA del modelo).

---

## 6. Trazabilidad checklist E6 ← marco S6·L ← deudas heredadas

| Origen | Item | Cómo aterriza en E6 |
|---|---|---|
| Marco §3 matriz dimensión × variante | C-T-* exclusivos a contratista/asbuilt | Verificado en tabla §2 |
| Marco §3 matriz dimensión × variante | C-Q-* exclusivos a diseño | Verificado en tabla §2 |
| Marco §4.2 criterio migración | 64% checks marcados IDS, 36% motor propio | Tabla §2 columna "Backend target" |
| Lección S5·X (L6 .gitignore) | Evidencias `_compliance_post_*` ya whitelisted | Sin acción nueva en S6 |
| Lección S5·X (L7 commit completo) | Patrón "1 bloque = 1 commit + push verificado" | Aplicar en cada bloque S6 |
| Deuda DT-S5L-02 (GlobalIds) | No bloquea E6 (no se autoría en S6) | Diferida a S6·X o S7·L |
| Deuda DT-S5X-01 (Bonsai) | Bonsai solo se usa para verificación visual opcional (C-G-02) | Sin actualizar |
| Deuda DF-02 (whitelist autoría) | No aplica a S6 (S6 es calidad, no autoría) | Diferida a S7·L o más adelante |

---

## 7. Sugerencias S6·X (miércoles 17/06) · pre-vista

Cuando ejecutemos S6·X aplicaremos esta checklist sobre FZK-Haus generando las evidencias §5. El bloque de hoy (S6·L) deja **todo el contrato cerrado**: marco + checklist + estructura motor + prototipo IDS.

S6·X arrancará con:
1. Implementar reglas motor propio (`quality_engine/rules/d*.py` mínimo viable) — al menos D1, D2, D3, D5.
2. Validar prototipo IDS con `ifctester` real sobre FZK-Haus.
3. Generar las matrices `_compliance_post_*` y `_compliance_ids_*` para ≥ 1 variante (idealmente las 4).
4. Generar los `audit_report_*.md` para las 4 variantes.

S6·S (sábado 20/06) será cierre formal E6: redacción del entregable síntesis `docs/E6_auditoria_calidad_fzk_haus.md` v1.0 + tag `e6-closed`.

---

**Fin de E6_checklist_calidad.md v1.0.**
