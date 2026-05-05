# Setup técnico · Checklist (hoy)

Marca cada paso al completarlo. Tiempo estimado: 60–90 min.

## 1. Entorno Python (10 min)
- [ ] Instalar Miniconda o Anaconda si no lo tienes
- [ ] `conda create -n openbim python=3.12 -y`
- [ ] `conda activate openbim`
- [ ] `conda install -c ifcopenshell -c conda-forge ifcopenshell -y`
- [ ] `pip install -r requirements.txt` (desde `openbim-12w/`)

## 2. Verificación (2 min)
- [ ] `python scripts/00_smoke_test.py` → todos los checks ✓
- [ ] Imprime "Setup OK" al final

## 3. Bonsai sobre Blender (15 min)
- [ ] Instalar [Blender 4.x](https://www.blender.org/download/) si no lo tienes
- [ ] Abrir Blender → Edit → Preferences → Get Extensions → buscar "Bonsai" e instalar
- [ ] Reiniciar Blender, verificar que aparece la pestaña Bonsai en la N-panel
- [ ] Referencia: [bonsaibim.org](https://bonsaibim.org)

## 4. Repos de muestra (5 min)
- [ ] `git clone https://github.com/buildingSMART/Sample-Test-Files` (junto a tu repo)
- [ ] `git clone https://github.com/buildingSMART/IDS` (releases v1.0.0)
- [ ] Abrir un IFC de muestra en Bonsai para confirmar que se ve

## 5. Cuentas y servicios (10 min)
- [ ] Cuenta en [IFC Validation Service](https://www.buildingsmart.org/users/services/validation-service/)
- [ ] Cuenta gratuita en [Speckle](https://speckle.systems) (la usarás en S11)
- [ ] Marcar en favoritos: [IFC 4.3.2 docs](https://ifc43-docs.standards.buildingsmart.org), [IfcOpenShell docs](https://docs.ifcopenshell.org)

## 6. Repo propio en GitHub (15 min)
- [ ] Crear repo `openbim-12w` en tu cuenta GitHub (privado)
- [ ] Desde la carpeta `openbim-12w/`: `git init && git add . && git commit -m "feat: initial scaffold"`
- [ ] `git remote add origin <url>` y `git push -u origin main`
- [ ] Verificar que el workflow de CI aparece en pestaña Actions (correrá en próximo push)

## 7. Confirmación final (1 min)
- [ ] Smoke test pasa
- [ ] Bonsai abre un IFC sin errores
- [ ] Repo en GitHub con CI configurado

Cuando todo esté ✅ → estás listo para la S1·L del lunes 11/05/2026 a las 07:30.

---

**Bloqueos típicos y solución rápida:**

| Síntoma | Solución |
|---|---|
| `conda: command not found` | Instalar [Miniconda](https://docs.conda.io/projects/miniconda/) |
| `import ifcopenshell` falla | Asegurar entorno activado: `conda activate openbim` |
| Bonsai no aparece en Blender | Versión Blender < 4.2 → actualizar |
| `git push` rechazado | Configurar SSH key o token PAT en GitHub |
