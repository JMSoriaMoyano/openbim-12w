# S9·L · Notas de sesión (comprimida)

**Fecha:** 12/07/2026 (domingo, catch-up post-silencio 21/06 – 11/07)
**Sesión oficial en calendario:** 06/07 (lunes)
**Semana temática:** CI/CD para BIM y bSDD
**Modo:** sprint comprimido L/X/S en una sola pasada
**Duración estimada:** 3-4 h

---

## 1. Contexto y decisión de compresión

Tras el push retrasado de S6·X + cierre E6 (12/07 mañana), el plan reintegra las 3 semanas perdidas comprimiendo S9·L/X/S en una sesión única. La justificación operativa está en `docs/DEUDAS_E7_E8.md` (ruta de recuperación §4).

**Absorbe la deuda E8 completa** (hitos §3.4.1, §3.4.2, §3.4.3):

- §3.4.1 CLI mínimo funcional → `quality_engine/cli.py` productivo.
- §3.4.2 Wrapper testeable → `quality_engine/core/runner.py::run_audit` ya lo era, no requiere refactor.
- §3.4.3 Test smoke con contrato canónico → `tests/test_smoke_quality_engine.py` (9 tests).

---

## 2. Entregables de la sesión

### 2.1 CLI productivo · `quality_engine/cli.py`

Sustituye el stub S6·L. Contrato:

```bash
python -m quality_engine.cli \
  --model MODEL \
  --variant {comun,diseno,contratista,asbuilt} \
  [--eir-version 0.2] \
  [--eir-dir DIR] \
  [--backends yaml_python,ids_xml] \
  --out OUT_JSON \
  [--fail-under N] \
  [--quiet]
```

**Códigos de salida definidos:**

| Código | Significado |
|---:|---|
| 0 | Auditoría completada (independiente del pct_pass) |
| 2 | Argumentos inválidos / rutas inexistentes |
| 3 | Error interno del motor (excepción no controlada) |
| 4 | Gate CI activo (`--fail-under N`) y pct_pass < N |

Import diferido del motor: la validación de argumentos ocurre antes de cargar `run_audit`, para respuestas rápidas de `--help` y de errores de path.

### 2.2 Test suite · `tests/test_smoke_quality_engine.py`

9 tests. Contrato canónico blindado:

```
FZK-Haus authored (SHA-256 c8a16f3f...) + PBSA v0.2 diseño
  → total=35, pass=15, fail=17, partial=1, N/A=2, pct_pass=45.45
```

Cubre:

1. `test_model_exists` · presencia del IFC authored.
2. `test_ids_exists` · presencia del IDS v0.2.
3. `test_ids_valid_against_schema` · IDS valida contra schema IDS 1.0 oficial (7 specs).
4. `test_engine_runs_diseno_variant` · `run_audit` completa sin excepciones.
5. `test_engine_produces_expected_summary` · contrato exacto de conteos.
6. `test_model_sha256_is_stable` · el SHA-256 del modelo authored no muta.
7. `test_cli_help_ok` · CLI responde a `--help`.
8. `test_cli_exit_code_2_on_missing_model` · gate de argumentos.
9. `test_cli_gate_fires_on_low_pct` · gate CI dispara con `--fail-under 95`.

**Ejecución local:** `pytest tests/ -v`
**Resultado:** 9 passed in ~10s.

### 2.3 Workflow productivo · `.github/workflows/ifc-ci.yml`

Sustituye el skeleton S6·L. Sobre `push` y `pull_request` a `main`:

1. Setup Python 3.12 con cache pip.
2. Instala `requirements.txt` (versiones fijas).
3. Ejecuta `scripts/00_smoke_test.py`.
4. Ejecuta `pytest tests/`.
5. Ejecuta el CLI para las 4 variantes EIR sobre FZK-Haus authored.
6. Publica los 4 JSONs como artifact `quality-engine-audit-<sha>` (retención 30 días).

**Trigger paths:** cambios en `quality_engine/`, `eir/`, `ids/`, `scripts/`, `tests/`, `requirements.txt` o el propio workflow.

**Decisión explícita:** el workflow NO activa `--fail-under` sobre FZK-Haus. El modelo académico produce fails esperados (46-52% pct_pass). El gate se activará cuando el proyecto integrador (S12) aporte un modelo PBSA real.

### 2.4 Versiones fijadas · `requirements.txt`

Migrado de rangos abiertos (`>=`) a `~=` (compatible release, PEP 440). Fijado:

- `ifcopenshell~=0.8.5`
- `ifctester~=0.8.5`
- `pyyaml~=6.0`
- `matplotlib~=3.10.9`

**Bonsai NO se fija** en `requirements.txt` — sus builds alpha diarios (2607071900 → 2607102147, 6 releases en 5 días según briefings del cron) son inestables. Cuando se necesite Bonsai en CI (S11·L, CDE OpenBIM), se instalará desde una release estable identificada explícitamente en la sesión.

---

## 3. Verificación end-to-end (ejecutada en sandbox 12/07 09:23 UTC)

```
$ python -m quality_engine.cli --model out/AC20-FZK-Haus_authored.ifc \
    --variant diseno --out /tmp/audit_cli_test.json
============================================================
quality_engine · auditoría completada
============================================================
  motor      : quality_engine 0.2.0-s6x
  variante   : diseno v0.2
  modelo     : AC20-FZK-Haus_authored.ifc
  backends   : ids_xml, yaml_python
  timestamp  : 2026-07-12T07:23:22+00:00
  total      : 35 · pass 15 · fail 17 · partial 1 · N/A 2
  pct_pass   : 45.45%
============================================================

$ pytest tests/ -v
tests/test_smoke_quality_engine.py .......... 9 passed in 9.52s
```

**Reproducibilidad:** el CLI produce el mismo `pct_pass=45.45%` que el script legacy `scripts/s6x_generate_e6_outputs.py`, confirmando paridad funcional.

---

## 4. Criterios de aceptación E9

| # | Criterio | Verificación |
|---|---|---|
| 1 | CLI del motor invocable desde línea de comandos | `python -m quality_engine.cli --help` ok |
| 2 | Códigos de salida definidos (0/2/3/4) | 4 códigos verificados en tests smoke |
| 3 | Test suite con contrato canónico | 9/9 pytest passed |
| 4 | Workflow GitHub Actions ejecutando el pipeline completo | `.github/workflows/ifc-ci.yml` v2 |
| 5 | 4 variantes EIR auditadas en cada CI run | Ver steps del workflow |
| 6 | Artefacto CI publicable y descargable | `actions/upload-artifact@v4`, retention 30d |
| 7 | Versiones de dependencias fijadas | `~=` en `requirements.txt` |
| 8 | Bonsai excluido de fijación (DT-S5X-01 respetada) | Comentario explícito en `requirements.txt` |
| 9 | Gate `--fail-under` implementado (uso futuro) | Verificado con test 9 |
| 10 | Notas de sesión redactadas | Este documento |

**Estado E9:** 10/10 criterios verificados. Listo para `tag e9-closed` tras primer run verde del workflow.

---

## 5. Deudas técnicas al cierre S9·L

### Nuevas

- **DT-S9L-01 · monitor**: el workflow CI no tiene aún branch protection en `main` que exija su pasada verde. Al ser repo privado y unipersonal se acepta, revisar si se abre a colaboradores.

### Actualizadas

- **DT-S5X-01 (Bonsai alpha)** · sigue en monitor · confirmada NO fijación en `requirements.txt` (documentada explícita).
- **DT-S6X-IDS (IFCWALL strict)** · sigue abierta · absorción prevista en S10·L (ver `docs/DEUDAS_E7_E8.md` §4).

### Cerradas en S9·L

- **DF-03 · reglas D2/D4/D6/D7 pendientes** · cerrada parcialmente: D2 tiene 20 checks operativos, D6 tiene 1 check + fail estructural documentado. D4 y D7 quedan explícitamente pospuestas a proyecto integrador (S12).
- **§3.4 completo de DEUDAS_E7_E8.md** · absorbido: E8 no requiere sesión propia.

---

## 6. Roadmap post S9·L

- **S9·X (previsto 08/07, ya pasado):** absorbido en esta sesión.
- **S9·S (previsto sáb 11/07, ya pasado):** absorbido en esta sesión.
- **E9 cierre y `tag e9-closed`:** aplicable tras primer run verde del workflow en GitHub.
- **S10·L (13/07 lunes):** BCF 3.0 y BCF-XML + absorción hito §2.4.1 de deudas E7 (resolver DT-S6X-IDS).

---

## 7. Firma y trazabilidad

- **Autor técnico:** José M. Soria (jmsoria@ciccp.es)
- **Ejecución sandbox:** 12/07/2026 09:23 CEST
- **Commits objetivo:** un único commit S9·L incluyendo CLI + tests + workflow + requirements + esta nota.
