# S6·L · Notas de sesión

**Fecha planificada:** Lunes 15/06/2026
**Fecha real ejecución:** Lunes 15/06/2026 (en plazo)
**Sesión:** S6·L · Calidad: qué validar y cómo
**Tema:** Marco 8D ISO 19650-2 + refactor motor modular + prototipo IDS
**Duración estimada:** ~3 h (5 bloques: A+B fusionados, C, D, E, F)
**Versión documento:** 1.0
**Estado E6:** En curso · 2 de 10 criterios verdes al cierre S6·L · cierre formal previsto S6·S (sábado 20/06).

---

## 1. Objetivos cumplidos

- [x] Establecer el **marco normativo interno de calidad BIM** organizado por las 3 capas de información de ISO 19650-2 (gráfica, no gráfica, documentación).
- [x] Definir las **8 dimensiones de calidad** (D1 Modelo, D2 Propiedades, D3 Relaciones, D4 Geometría, D5 Unidades, D6 Clasificación, D7 Temporal 4D, D8 Coste 5D).
- [x] Documentar la **matriz dimensión × variante EIR v0.2** que materializa la directiva 4D=contratista / 5D=diseño.
- [x] Establecer el **criterio de migración a IDS v1.0**: ~64% de checks E6 son migrables a IDS, ~36% queda en motor propio.
- [x] **Refactorizar el motor de calidad** a estructura modular `quality_engine/` (18 ficheros, 604 líneas de skeleton).
- [x] Redactar la **checklist completa E6** con 28 checks únicos identificados y trazables.
- [x] Generar **prototipo IDS XML v1.0** funcional con 2 reglas validables (C-P-01, C-P-03).
- [x] Validar end-to-end en sandbox + local del usuario: estructura `quality_engine/` importa limpia, CLI parser funciona, prototipo IDS bien formado.

---

## 2. Bloques ejecutados

### 2.1 Bloque A+B · Marco de calidad + decisión IDS (fusionados)

Se fusionaron en un único documento porque se complementaban: el marco define **qué se valida** y la decisión IDS define **cómo se valida**.

**Documento producido:** `docs/S6L_marco_calidad.md` v1.0 (273 líneas, 8 secciones H2).

**Decisiones clave de diseño:**

- **Q1 = B** · Alcance: 6 dimensiones + 4D + 5D (8 total) en lugar de solo las 6 sugeridas por el briefing matinal.
- **Ordenación dimensiones** por capa ISO 19650-2 (no por tipo de objeto BIM): más rigurosa, alineada con el plan formativo que arranca desde ISO 19650.
- **D1 (Modelo) y D5 (Unidades)** ubicadas en **capa no gráfica** (decisión del usuario): son metadatos declarativos, no objetos representables. La capa gráfica queda exclusivamente para D4 Geometría.
- **Q2 = B** · Motor: refactor modular real (no solo renombrado). Estructura ejecutada en Bloque D.
- **Q3 = B** · IDS: prototipo mínimo redactado hoy como continuidad natural hacia S7·L (no sorpresa).

**Matriz dimensión × variante (resumen):**

| Dimensión | común | diseño | contratista | asbuilt |
|---|---|---|---|---|
| D1-D6 | ✅ obligatorias en todas | ✅ | ✅ | ✅ |
| D7 (4D) | ⚪ no aplica | ⚪ opcional | ✅ obligatoria | ✅ obligatoria (hitos) |
| D8 (5D) | ⚪ no aplica | ✅ obligatoria | ⚪ opcional | ⚪ no aplica |

**Distribución global checks:** 64% IDS · 36% motor propio.

**Duración:** ~45 minutos.

### 2.2 Bloque C · Checklist E6

**Documento producido:** `docs/E6_checklist_calidad.md` v1.0 (288 líneas, 7 secciones).

**Decisiones de diseño:**

- **Q-C1 = c** · Formato híbrido: introducción + tabla resumen 28 checks + apartados por dimensión con detalle.
- **Q-C2 = a** · Aplicación sobre **FZK-Haus**: modelo conocido, reproducible, evidencias trazables a E4/E5.

**Codificación checks:**

- `C-M-*` Modelo · 6 checks
- `C-P-*` Propiedades · 5 checks
- `C-R-*` Relaciones · 3 checks
- `C-G-*` Geometría · 3 checks
- `C-U-*` Unidades · 3 checks
- `C-C-*` Clasificación · 2 checks
- `C-T-*` Temporal · 3 checks (solo contratista + asbuilt)
- `C-Q-*` Coste · 3 checks (solo diseño)

**Aplicabilidad por variante:** común 22 · diseño 25 · contratista 24 · asbuilt 24.

**10 criterios de aceptación E6 establecidos**, con 2 verdes al cierre S6·L (marco + checklist) y 8 progresivos a S6·X + S6·S.

**Insight clave registrado:** **previsión honesta de fails sobre FZK-Haus**. Esperamos:
- D6 Clasificación → `fail` en ambos checks (FZK-Haus no tiene clasificación).
- D7 Temporal → `fail` en C-T-01/02/03 (modelo sin 4D).
- D8 Coste → `fail/partial` en C-Q-* (Qto_* parciales).

Esto **NO es defecto del marco**, es el marco detectando gaps reales del modelo de muestra. La aplicación práctica a un modelo PBSA propio en sesiones posteriores resolverá estos gaps.

**Duración:** ~30 minutos.

### 2.3 Bloque D · Refactor `quality_engine/` modular

**Decisiones de diseño:**

- **Q-D1 = a** · Solo stubs/skeleton, sin implementación. La implementación viene en S6·X.
- **Q-D2 = a** · `scripts/s4s_audit_eir.py` intacto. El nuevo `quality_engine/` crece en paralelo. Cero riesgo de regresión.

**Estructura creada (18 ficheros · 604 líneas):**

```
quality_engine/
├── __init__.py                        v0.1.0-stub · status=skeleton
├── cli.py                             entrypoint con argparse completo
├── core/
│   ├── __init__.py
│   ├── result.py                      ResultadoCheck dataclass + tipos Literal
│   ├── merger.py                      CheckIdCollisionError + merge_eir()
│   └── runner.py                      run_audit() + consolidate_results()
├── backends/
│   ├── __init__.py
│   ├── yaml_python.py                 run_yaml_python_backend()
│   └── ids_xml.py                     run_ids_backend()
└── rules/
    ├── __init__.py
    ├── d1_modelo.py                   2 stubs (C-M-01, C-M-02)
    ├── d2_propiedades.py              2 stubs genéricos
    ├── d3_relaciones.py               3 stubs (C-R-01/02/03)
    ├── d4_geometria.py                2 stubs (C-G-02/03)
    ├── d5_unidades.py                 3 stubs (C-U-01/02/03)
    ├── d6_clasificacion.py            2 stubs (C-C-01/02)
    ├── d7_temporal.py                 3 stubs (C-T-01/02/03)
    └── d8_coste.py                    3 stubs (C-Q-01/02/03)
```

**Detalles de diseño aplicados:**

- `ResultadoCheck` dataclass con tipos `Literal` para `status`/`layer`/`dimension`/`backend` (seguridad de tipos sin overhead).
- `CheckIdCollisionError` extiende `ValueError`: fail-fast explícito heredado del contrato S5·X.
- Cada stub lanza `NotImplementedError` con mensaje "S6·X · ..." (trazabilidad clara de qué falta).
- Cada módulo `d*.py` documenta en docstring los check_ids cubiertos, backend target, capa ISO y variantes aplicables.

**Entrega:** zip único `quality_engine_skeleton.zip` (22 entradas, 19.7 KB) descargado y extraído en local del usuario sin issues.

**Smoke test sandbox + local: ambos PASS.**

**Duración:** ~50 minutos.

### 2.4 Bloque E · Prototipo IDS XML

**Decisión de diseño:**

- **Q-E1 = a** · 2 reglas mínimas viables (no 4-5). Demostración del patrón antes de ampliar.

**Documento producido:** `ids/PBSA_v0.2_prototype.ids` v0.1.0 (115 líneas, 4.8 KB).

**Reglas implementadas:**

| ID | Entidad | Pset | Propiedad | Backend |
|---|---|---|---|---|
| **C-P-01** | IfcWall | Pset_WallCommon | Reference (ancla) | IDS nativo |
| **C-P-03** | IfcDoor | Pset_DoorCommon | FireRating | IDS nativo |

**Detalles técnicos:**

- Namespace: `http://standards.buildingsmart.org/IDS` (oficial buildingSMART).
- Schema location: `http://standards.buildingsmart.org/IDS/1.0/ids.xsd`.
- Info block completo: title, copyright (NEXUM), version, description, author, date, purpose, milestone.
- Cardinalidad: `minOccurs=1 maxOccurs=unbounded` en applicability (todos los productos del modelo aplican).
- `dataType=IFCLABEL` y `cardinality=required` en cada property requirement.
- Comentarios XML en cada spec con metadatos: dimensión, capa ISO, variantes, backend, cardinalidad.
- Nota histórica embebida en C-P-03 sobre el cambio 40%→100% de E5.

**Validación end-to-end:**

- Sandbox: XML well-formed (xml.etree.ElementTree) + estructura conforme IDS v1.0 (parsing con namespace correcto + extracción de info + 2 specifications + applicability + requirements). **PASS**.
- Local del usuario: `python -c "...findall(specification)" ` devuelve `specs: 2`. **PASS**.

**Detalle de diseño registrado:** C-P-01 exige `Pset_WallCommon.Reference` (propiedad ancla estándar del Pset) en lugar de "Pset presente". El schema IDS v1.0 **obliga** a especificar al menos una propiedad concreta dentro del Pset, no admite chequeo de presencia del Pset entero como tal. Patrón estándar de la industria IDS.

**Duración:** ~25 minutos.

### 2.5 Bloque F · Notas de sesión

**Documento producido:** `docs/S6L_notas_sesion.md` (este fichero).

**Duración:** ~15 minutos.

---

## 3. Hallazgos y aprendizajes

### 3.1 Técnicos

1. **`raise` directo en `main()` rompe `--help`** de argparse. Patrón a evitar en todo CLI con stubs:
   - **Mal:** `def main(): raise NotImplementedError()` → `--help` lanza la excepción antes de mostrar ayuda.
   - **Bien:** `def main(): parser.parse_args(); raise NotImplementedError()` → argparse intercepta `--help` y sale con exit 0 antes de llegar al `raise`.
   - Bug detectado en local del usuario tras extraer el zip. Fix aplicado a `cli.py` y revalidado. No queda como deuda, es fix puntual ya resuelto.

2. **IDS v1.0 no admite chequeo de "Pset presente sin propiedad concreta".** Para validar presencia de un Pset hay que elegir una propiedad ancla (típicamente `Reference` o cualquier propiedad estándar del Pset según IFC4 spec). Esto es **limitación del estándar IDS**, no de nuestro motor.

3. **El patrón modular `core / backends / rules` es robusto** para motor multi-backend. Permite añadir backends futuros (ej. SHACL, JSON-LD) sin tocar las reglas, y migrar reglas individuales entre backends sin romper la API pública.

4. **Tipos `Literal` en Python ≥ 3.8** son la forma más limpia de declarar enums sin overhead. `CheckStatus = Literal["pass", "fail", "partial", ...]` da validación estática con mypy y autocompletado IDE sin necesidad de `Enum` clase.

### 3.2 Proceso

5. **Fusionar Bloque A+B en un único documento** funcionó: el marco y la decisión IDS son inseparables conceptualmente. Re-evaluar este patrón en sesiones futuras cuando dos bloques se solapen mucho.

6. **El patrón "1 zip = N ficheros" funciona mejor que "N download/share individuales"** cuando se entrega una estructura modular completa. Lo hemos usado por primera vez en S6·L y reduce drásticamente el riesgo de colocar un fichero en la subcarpeta equivocada.

7. **Validar el extract del zip con 3 comandos (`dir`, `import`, `--help`) inmediatamente después** detectó el bug del `--help` antes de hacer commit. Disciplina a mantener.

### 3.3 Deuda formativa / técnica abierta tras S6·L

| ID | Estado | Descripción | Target |
|---|---|---|---|
| DT-S5L-02 | Abierta | GlobalIds no deterministas en autoría — política de seed | S6·X o S7·L |
| DT-S5X-01 | Abierta · monitor | Bonsai 0.8.6-alpha unstable — no actualizar | Revisita en release estable |
| DF-02 (potencial) | Abierta | Whitelist §3 ampliación (geometría existente, borrado, relaciones espaciales) | S7·L |
| **DF-03** (nueva) | **Abierta · S6·X** | Implementar reglas reales en `quality_engine.rules.d*_*.py` (skeleton hoy → ejecutable miércoles) | S6·X |
| **DF-04** (nueva) | **Abierta · S6·X** | Migrar lógica de merge desde `scripts/s4s_audit_eir.py` a `quality_engine.core.merger` | S6·X |
| **DF-05** (nueva) | **Abierta · S6·X** | Ampliar prototipo IDS de 2 a ~15 reglas (todas las migrables según marco §4.2) | S6·X o S7·L |

---

## 4. Artefactos producidos en S6·L

| Tipo | Ruta | Tamaño / Notas | Bloque |
|---|---|---|---|
| Doc | `docs/S6L_marco_calidad.md` | 273 líneas · marco 8D ISO 19650-2 + decisión IDS | A+B |
| Doc | `docs/E6_checklist_calidad.md` | 288 líneas · 28 checks + 10 criterios aceptación | C |
| Code | `quality_engine/__init__.py` | v0.1.0-stub | D |
| Code | `quality_engine/cli.py` | argparse + main() (fix --help) | D |
| Code | `quality_engine/core/result.py` | ResultadoCheck + tipos Literal | D |
| Code | `quality_engine/core/merger.py` | CheckIdCollisionError + merge_eir() stub | D |
| Code | `quality_engine/core/runner.py` | run_audit() + consolidate_results() stubs | D |
| Code | `quality_engine/backends/yaml_python.py` | run_yaml_python_backend() stub | D |
| Code | `quality_engine/backends/ids_xml.py` | run_ids_backend() stub | D |
| Code | `quality_engine/rules/d1_modelo.py` | 2 stubs (C-M-01/02) | D |
| Code | `quality_engine/rules/d2_propiedades.py` | 2 stubs genéricos | D |
| Code | `quality_engine/rules/d3_relaciones.py` | 3 stubs (C-R-01/02/03) | D |
| Code | `quality_engine/rules/d4_geometria.py` | 2 stubs (C-G-02/03) | D |
| Code | `quality_engine/rules/d5_unidades.py` | 3 stubs (C-U-01/02/03) | D |
| Code | `quality_engine/rules/d6_clasificacion.py` | 2 stubs (C-C-01/02) | D |
| Code | `quality_engine/rules/d7_temporal.py` | 3 stubs (C-T-01/02/03) | D |
| Code | `quality_engine/rules/d8_coste.py` | 3 stubs (C-Q-01/02/03) | D |
| Code | `quality_engine/{core,backends,rules}/__init__.py` | 4 `__init__.py` de subpaquetes | D |
| IDS | `ids/PBSA_v0.2_prototype.ids` | 115 líneas · 2 specs (C-P-01, C-P-03) | E |
| Doc | `docs/S6L_notas_sesion.md` | este fichero | F |

**Total artefactos:** 21 ficheros nuevos · 0 modificados (auditor legacy intacto).

---

## 5. Trazabilidad commit-a-evidencia (prevista)

| Commit (pendiente) | Bloque | Evidencias |
|---|---|---|
| (pendiente push hoy) | A+B+C+D+E+F | 21 ficheros nuevos: 3 docs + 18 código + 1 IDS |

Decisión del usuario: **acumular y pushear al cierre de S6·L** (no commits intermedios). Un único commit para toda la sesión.

---

## 6. Estado de avance hacia E6 (sábado 20/06)

10 criterios de aceptación según `E6_checklist_calidad.md §4`:

| # | Criterio | Estado tras S6·L |
|---|---|---|
| 1 | `docs/S6L_marco_calidad.md` v1.0 firmado | ✅ |
| 2 | `docs/E6_checklist_calidad.md` v1.0 firmado | ✅ |
| 3 | `quality_engine/` estructura modular creada | ✅ (stubs · S6·X completa implementación) |
| 4 | `ids/PBSA_v0.2_prototype.ids` con ≥ 2 reglas IDS válidas | ✅ (validable con `ifctester` en S6·X) |
| 5 | Matrices `_compliance_post_<variante>.json` regeneradas con marco v1.0 (4 variantes) | ⏳ S6·X |
| 6 | `audit_report_<variante>.md` generado para las 4 variantes | ⏳ S6·X |
| 7 | `_compliance_ids_*.json` con resultado backend IDS (≥ 1 variante) | ⏳ S6·X |
| 8 | `docs/E6_auditoria_calidad_fzk_haus.md` v1.0 (entregable síntesis) | ⏳ S6·S |
| 9 | `S6L_notas_sesion.md`, `S6X_notas_sesion.md`, `S6S_notas_sesion.md` redactadas | 🟡 1/3 (este fichero) |
| 10 | Tag `e6-closed` sobre commit final | ⏳ S6·S |

**Estado E6 = 4/10 verdes + 1 amarillo + 5 pendientes.** Lunes ha cerrado todo el contrato (qué se valida + cómo + estructura motor + prototipo IDS). Miércoles ejecuta. Sábado redacta y firma.

---

## 7. Próxima sesión · S6·X (Miércoles 17/06/2026)

Sesión de implementación del motor + ejecución sobre FZK-Haus. Plan:

1. **Implementar reglas motor propio** (`quality_engine.rules.d*_*.py`):
   - Mínimo viable: D1 (C-M-01/02), D3 (C-R-01/02/03), D5 (C-U-01/02/03), D8 sniff (C-Q-03).
   - Resto opcional si hay tiempo: D2 fallback, D4, D6, D7.
2. **Migrar lógica de merge** desde `scripts/s4s_audit_eir.py` a `quality_engine.core.merger` (DF-04).
3. **Implementar `runner.run_audit()`** completo: cargar EIR + cargar modelo + ejecutar backends + consolidar matriz.
4. **Implementar backend IDS** (`backends/ids_xml.py`) invocando `ifctester` real contra el prototipo.
5. **Ejecutar sobre FZK-Haus** y generar:
   - `out/AC20-FZK-Haus_compliance_post_<variante>.json` × 4 variantes (motor propio v1.0)
   - `out/AC20-FZK-Haus_compliance_ids_<variante>.json` × ≥ 1 variante (backend IDS)
   - `out/AC20-FZK-Haus_audit_report_<variante>.md` × 4 variantes (resúmenes humanos)
6. **Ampliar prototipo IDS** de 2 a ~15 reglas (DF-05, opcional según tiempo · puede diferirse a S7·L).
7. **Documentar todo en** `docs/S6X_notas_sesion.md`.

S6·S (sábado 20/06) será cierre formal E6: redacción de `docs/E6_auditoria_calidad_fzk_haus.md` v1.0 + tag `e6-closed`.

---

**Fin de S6L_notas_sesion.md v1.0.**
