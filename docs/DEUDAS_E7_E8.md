# Deudas formales · E7 y E8

**Fecha de emisión:** 12/07/2026 (S9·S)
**Autor:** José M. Soria (jmsoria@ciccp.es)
**Contexto:** durante el periodo 21/06 – 11/07 no se ejecutaron las sesiones S7·L/X/S ni S8·L/X/S del plan formativo OpenBIM 12w. Los entregables E7 y E8 no se han cerrado en fecha. Este documento formaliza la deuda, define hitos mínimos irrenunciables y traza la ruta de recuperación sin comprometer la coherencia del cierre del plan.

---

## 1. Principio de gestión de la deuda

**Regla:** no arrastrar carga oculta al cierre del plan. Toda sesión omitida se documenta explícitamente aquí con:

- Qué se perdió (alcance previsto).
- Qué es irrenunciable (hitos que si no se ejecutan, rompen entregables posteriores).
- Qué se sacrifica (didáctica, exhaustividad, cobertura no crítica).
- Cuándo se recupera (integración diferida).

**No hay reejecución completa de S7 ni S8.** Se aplica el criterio de **impacto sobre cadena de dependencias**: sólo se recupera lo que otra sesión posterior requiere.

---

## 2. E7 · IDS v1.0: conceptos y XML

### 2.1 Alcance original (previsto para sábado 27/06)

Semana S7 iba a profundizar en el estándar IDS 1.0 de buildingSMART como formato XML normalizado para expresar requisitos de información. Ampliar el prototipo IDS de 7 → ~15 specs, cubriendo dimensiones D2/D4/D6/D7. Documentar patrones de aplicabilidad (`<ids:applicability>`), requisitos (`<ids:requirements>`), cardinalidades y facets (`entity`, `attribute`, `classification`, `property`, `material`).

**Entregable E7 previsto:** `docs/E7_ids_prototype_v0.3.md` + `ids/PBSA_v0.3_prototype.ids` con 15 specs validadas.

### 2.2 Estado real al 12/07

- **Motor ya soporta IDS:** `quality_engine/backends/ids_xml.py` funcional con `ifctester>=0.8` desde S6·X.
- **IDS v0.2 vigente:** 7 specs (`ids/PBSA_v0.2_prototype.ids`), todas validadas contra schema oficial IDS 1.0.
- **Deuda técnica DT-S6X-IDS abierta** desde 17/06: `IFCWALL` strict no captura `IfcWallStandardCase`. Sin resolver.

### 2.3 Impacto sobre E9-E12

| Entregable posterior | ¿Necesita E7 completo? | Justificación |
|---|---|---|
| E9 (CI/CD) | **NO** | CI valida el IDS que exista; 7 specs son suficientes para pipeline funcional |
| E10 (BCF 3.0) | NO | BCF es canal de retorno, agnóstico del volumen de specs |
| E11 (CDE) | PARCIAL | La federación en Speckle/Bonsai muestra checks IDS — 7 basta para demo |
| E12 (proyecto integrador) | **SÍ (parcial)** | Recomendable llevar ~12-15 specs al proyecto integrador para credibilidad técnica |

### 2.4 Hitos irrenunciables (a integrar en S10·X o S11·X)

1. **Resolver DT-S6X-IDS**: definir specs explícitas para `IfcWall` + `IfcWallStandardCase` (y análogo para `IfcSlab`/`IfcSlabStandardCase` y `IfcColumn`/`IfcColumnStandardCase` si el modelo los introduce). **Sin esto E12 pierde credibilidad.**
2. **Añadir 3-5 specs D6 (clasificación bSDD)**: hoy D6 tiene 1 sola regla en yaml_python (fail estructural). Al menos cubrir clasificación de `IfcWall`, `IfcSlab`, `IfcDoor` con `<ids:classification>`.
3. **Documentar patrones IDS en `docs/S7L_ids_patrones.md`** (versión mini, ~80 líneas): applicability vs requirements, cardinality, facets básicos. Sirve de referencia para el proyecto integrador.

### 2.5 Sacrificios asumidos

- **Sin ampliación a 15 specs completa.** Objetivo revisado: 10-12 specs para cierre del plan.
- **Sin cobertura D4 (planificación/4D) en IDS.** Se mantiene deuda técnica indefinida — el 4D IDS es tema avanzado, no crítico para el sprint formativo.
- **Sin sesión narrativa de conceptos IDS.** El aprendizaje se hará al hilo de resolver los hitos §2.4, no como sesión dedicada.

### 2.6 Estado formal

**E7 = DEUDA · no se emite tag `e7-closed`.** Los hitos §2.4 se absorberán en E10 o E11 y se documentarán en las notas de la sesión correspondiente.

---

## 3. E8 · `ifctester` (Python) e integración

### 3.1 Alcance original (previsto para sábado 04/07)

Semana S8 iba a integrar `ifctester` como backend Python productivo, sustituyendo el uso via XML por invocación directa desde el motor. Definir capas: `runner` → `backends/ids_xml.py` → `ifctester.reporter`. Cobertura de tests unitarios sobre el backend. Modo CLI: `python -m quality_engine.cli audit --model X.ifc --ids Y.ids`.

**Entregable E8 previsto:** `docs/E8_ifctester_integracion.md` + `quality_engine/cli.py` funcional + suite de tests mínima.

### 3.2 Estado real al 12/07

- **`ifctester>=0.8` ya declarado** en `requirements.txt` (S6·X).
- **`backends/ids_xml.py` funcional** — ejecutando 7 specs contra FZK-Haus con resultados coherentes (§4-5 del informe E6).
- **CLI existe como `quality_engine/cli.py`** en el skeleton pero no productivizada.
- **Sin tests unitarios** sobre el backend.

### 3.3 Impacto sobre E9-E12

| Entregable posterior | ¿Necesita E8 completo? | Justificación |
|---|---|---|
| E9 (CI/CD) | **SÍ (parcial)** | El workflow GitHub Actions invocará el backend — necesita ser invocable de forma limpia |
| E10 (BCF 3.0) | NO | BCF opera sobre issues, no sobre pipeline |
| E11 (CDE) | NO | Speckle/Bonsai no dependen del CLI |
| E12 (proyecto integrador) | **SÍ** | El proyecto integrador demuestra el pipeline end-to-end — CLI reproducible es crítico |

### 3.4 Hitos irrenunciables (a integrar en S9·L/X)

1. **CLI mínimo funcional**: `python -m quality_engine.cli audit --model X.ifc --eir Y.yaml --variant diseno --out Z.json`. Sin esto E9 (CI/CD) no tiene qué ejecutar de forma limpia.
2. **Wrapper testeable de `ids_xml.py`**: función pura `run_ids_validation(model_path, ids_path) -> List[CheckResult]` invocable sin efectos secundarios.
3. **1 test smoke**: dado FZK-Haus + `PBSA_v0.2_prototype.ids`, el backend devuelve 7 CheckResult con el mismo status que el output S6·X. **Este test blindaría toda regresión futura.**

### 3.5 Sacrificios asumidos

- **Sin suite de tests completa** sobre reglas Python. Se acepta cobertura mínima (1 test smoke).
- **Sin cobertura de casos edge** (IDS malformado, modelo corrupto, etc.). Se maneja con try/except genérico.
- **Sin documentación narrativa de `ifctester`.** El aprendizaje se hace leyendo el propio módulo cuando haga falta.

### 3.6 Estado formal

**E8 = DEUDA · no se emite tag `e8-closed`.** Los hitos §3.4 se absorberán en E9 (CI/CD) y se documentarán en `docs/S9L_notas_sesion.md`.

---

## 4. Ruta de recuperación integrada

| Semana | Sesión | Contenido oficial | Deuda absorbida |
|---|---|---|---|
| S9 | L/X/S | CI/CD para BIM y bSDD | **E8 hitos §3.4 completos** |
| S10 | L/X/S | BCF 3.0 y BCF-XML | E7 hito §2.4.1 (DT-S6X-IDS) |
| S11 | L/X/S | CDE OpenBIM: Speckle, Bonsai, federación | E7 hito §2.4.2 (D6 IDS) + §2.4.3 (docs patrones) |
| S12 | L/X/S | FINAL: proyecto integrador | Verificar cierre de toda deuda residual |

**Consecuencia práctica:** las sesiones S9 a S11 llevarán carga adicional (+15% de trabajo estimado por sesión). Se compensa reduciendo la profundidad narrativa/didáctica en cada una y priorizando output ejecutable.

---

## 5. Riesgos

| Riesgo | Probabilidad | Impacto | Mitigación |
|---|---|---|---|
| S10-S11 se retrasan por sobrecarga | media | alta | Reducir alcance narrativo, priorizar hitos §2.4 y §3.4 |
| E12 llega con IDS insuficiente (<10 specs) | baja | media | Congelar en 10 specs mínimo el sábado de S11 |
| Nuevas deudas técnicas aparecen en S10/S11 | media | media | Bloque de 30 min al inicio de S12·L para triaje |
| El CI de E9 no consume el IDS por bug del CLI | baja | alta | Test smoke §3.4.3 protege contra esto |

---

## 6. Compromisos

1. **Este documento se versiona en el repo** como fuente única de verdad sobre lo pospuesto.
2. **Los hitos irrenunciables §2.4 y §3.4 se marcan explícitamente en las notas de S9/S10/S11** cuando se ejecuten, con referencia a esta deuda.
3. **En S12·L se ejecuta triaje** de deuda residual antes de arrancar el proyecto integrador.
4. **Si al cierre del plan (01/08) queda deuda técnica abierta**, se documenta en `docs/PLAN_CIERRE_deudas_residuales.md` con roadmap post-plan.

---

## 7. Referencia cruzada

- Informe E6: `docs/E6_auditoria_calidad_fzk_haus.md` (§9 Deudas técnicas).
- Notas S6·X: `docs/S6X_notas_sesion.md`.
- Deuda técnica IDS: DT-S6X-IDS (abierta, ver §3 de E6).
- Deuda técnica Bonsai: DT-S5X-01 (monitor, ver §9 de E6).

---

**Firma:** J.M. Soria · 12/07/2026 (S9·S catch-up)
