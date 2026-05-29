# E3 — Checklist de cierre (binario, auto-verificable)

> Marca cada caja `[ ]` → `[x]` cuando completes el punto. Un E3 cerrado
> tiene **todos** los checks marcados. Si alguno no aplica, marca `[N/A]` y
> justifica al final.

## Pre-requisitos (antes de empezar a escribir)

- [ ] El venv está activo (prompt muestra `(.venv)`)
- [ ] `pip list | grep ifcopenshell` muestra `ifcopenshell 0.8.5`
- [ ] `models/samples/_local/AC20-FZK-Haus.ifc` existe en disco local
- [ ] `git status` reporta working tree clean (HEAD sincronizado con remote)
- [ ] `git log --oneline -5` muestra al menos los commits S3L + S3X-A + S3X-B + S3X-C

## Ejecución del script

- [ ] `python scripts/s3l_ifc_inspect.py` se ejecuta sin errores
- [ ] Consola muestra `[OK] Informe guardado en: out/S3X_lab_run_<timestamp>.md`
- [ ] El informe generado tiene 8 secciones (HEADER, Pirámide, Conteo, Validación,
      Auditoría Pset, Anatomía muro, Pendientes)
- [ ] La sección "Validación cruzada" reporta **22 OK · 0 FAIL · 22 total**
- [ ] La sección "Auditoría Pset NEXUM" reporta **0 OK · 40 no conformes · 0%**

## Entregable principal

- [ ] `docs/E3_auditoria_fzk_haus.md` existe en el repo
- [ ] Sección 1 (Datos del modelo) completa: 9 campos rellenos con valores reales
- [ ] Sección 2 (Estructura espacial) tiene tu análisis crítico (no solo la tabla)
- [ ] Sección 3 (Inventario físico) explica el "+1" entre IfcOpeningElement (17)
      y los rellenos (16) o referencia explain_entity para localizarlo
- [ ] Sección 4 (Inventario relacional) calcula el ratio boundaries/IfcSpace
      (81 / 7 = ~11.6)
- [ ] Sección 5 (Caso muro #15042) tiene análisis razonado del cumplimiento
      de las 3 restricciones de IfcWallStandardCase
- [ ] Sección 6 (Auditoría Pset) tiene tu interpretación NEXUM (no solo cifras)
- [ ] Sección 7 (Conformidad final) tiene veredicto razonado SÍ/NO/CONDICIONADO
- [ ] Sección 8 (Lecciones Can Cabassa) tiene 3-5 puntos extrapolables

## Evidencia versionada

- [ ] El informe `out/S3X_lab_run_<timestamp>.md` más reciente se renombra a
      `out/E3_lab_run.md`
- [ ] El renombrado se commitea (forzar con `git add -f out/E3_lab_run.md` porque
      `out/*.md` está en `.gitignore` salvo `.gitkeep` y este fichero)
- [ ] `docs/E3_cierre.md` está relleno (no es plantilla)

## Comprobaciones de calidad del texto

- [ ] Cada afirmación numérica está respaldada por una cifra del informe
- [ ] No hay "TODO" pendientes en `docs/E3_auditoria_fzk_haus.md`
- [ ] No hay placeholders `(rellenar)` ni `<!-- ... -->` en el texto final
- [ ] Todas las referencias cruzadas a otras dudas (D3-01, D3-02, D3B-01,
      D3B-02) son consistentes con `docs/S3X_dudas_resueltas.md`
- [ ] Las URLs externas (buildingSMART, etc.) abren correctamente

## Commit final

- [ ] `git add docs/E3_auditoria_fzk_haus.md docs/E3_cierre.md`
- [ ] `git add -f out/E3_lab_run.md`
- [ ] `git status` muestra exactamente esos 3 ficheros stageados
- [ ] `git commit -m "E3: auditoria informacional FZK-Haus + lab_run + cierre"`
- [ ] `git push origin main`
- [ ] Crear tag de cierre: `git tag e3-closed && git push origin e3-closed`

## Verificación post-cierre

- [ ] Visitar https://github.com/JMSoriaMoyano/openbim-12w y comprobar que el
      tag `e3-closed` está presente
- [ ] El README puede mostrar el tag en su sección de hitos (opcional)
- [ ] El cron `6ffa9c6f` del lunes 01/06 07:00 CEST verá el repo en estado
      `e3-closed` (semana 4 arranca con S4·L)

---

## Justificaciones N/A

<!-- Si has marcado algún check como [N/A], justifícalo aquí en 1-2 frases. -->

## Tiempo invertido

<!-- Apunta cuánto tiempo te llevó cada bloque para calibrar mejor E4 en
adelante. Útil para el meta-cierre. -->

| Bloque | Tiempo |
|---|---|
| Pre-requisitos + ejecución script | … |
| Redacción secciones 1-2 | … |
| Sección 5 (muro #15042, nivel medio) | … |
| Sección 6 (auditoría Pset, interpretación) | … |
| Sección 7-8 (veredicto + lecciones) | … |
| Commit + push + tag | … |
| **Total** | … |
