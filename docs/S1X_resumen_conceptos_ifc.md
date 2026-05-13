# S1·X · Resumen conceptual del estándar IFC

Sesión del miércoles 13/05/2026 · Lab: primer contacto IFC + IfcOpenShell.
Este documento recoge **únicamente conceptos del estándar IFC** aprendidos hoy, sin entrar en herramientas (Bonsai, IfcOpenShell) ni en código. Es la base teórica que se materializará en S3 (IFC schema), S4–S5 (autoría) y S6 (calidad).

---

## 1. Qué es IFC

**IFC** (Industry Foundation Classes) es un **modelo de datos abierto** publicado por buildingSMART y ratificado como norma **ISO 16739-1:2024** (versión actual estable: **IFC 4.3.2**). Su propósito es representar **cualquier elemento de un edificio o infraestructura** de manera independiente del software que lo creó.

IFC tiene tres planos que conviven en el mismo fichero pero conviene distinguir mentalmente:

| Plano              | Naturaleza                                                                                          |
| ------------------ | --------------------------------------------------------------------------------------------------- |
| **Esquema**        | La "gramática": diccionario de ~700 clases y relaciones, definido en lenguaje EXPRESS.              |
| **Instancia**      | Un fichero `.ifc` concreto que describe un proyecto real usando esa gramática.                      |
| **Implementación** | Cómo cada software (Revit, ArchiCAD, Tekla…) escribe y lee ficheros IFC. Aquí está el 90% de líos.  |

Formatos físicos del fichero: `.ifc` (texto STEP, el más común), `.ifcXML`, `.ifczip`.

---

## 2. Las tres capas de información en un IFC

Todo IFC tiene **tres capas conceptuales** que coexisten:

| Capa                | Para qué sirve                          | Ejemplos                                         |
| ------------------- | --------------------------------------- | ------------------------------------------------ |
| **Capa espacial**   | Localiza las cosas en el mundo          | `IfcProject` → `IfcSite` → `IfcBuilding` → `IfcBuildingStorey` → `IfcSpace` |
| **Capa física**     | Las cosas construidas (productos)       | `IfcWall`, `IfcSlab`, `IfcRoof`, `IfcWindow`, `IfcFurniture`, `IfcChimney` |
| **Capa de tipos**   | Plantillas / catálogo de productos      | `IfcWallType`, `IfcSlabType`, `IfcWindowType`, `IfcSpaceType`              |

Las tres capas se **conectan entre sí** mediante objetos de relación (`IfcRelContainedInSpatialStructure`, `IfcRelDefinesByType`, `IfcRelAggregates`, etc.) que se estudiarán formalmente en **S3**.

---

## 3. La jerarquía espacial canónica

Es la **columna vertebral** de cualquier IFC bien formado:

```
IfcProject              ← raíz (siempre exactamente 1)
 └── IfcSite            ← terreno / parcela / emplazamiento
      └── IfcBuilding   ← edificio físico
           └── IfcBuildingStorey   ← planta horizontal
                ├── IfcSpace       ← espacios funcionales (habitaciones)
                └── elementos físicos (IfcWall, IfcSlab, IfcDoor, …)
```

### 3.1 · IfcProject

- **Único y obligatorio** por fichero. Más de uno o ninguno = IFC corrupto.
- Guarda: nombre del proyecto, sistema de unidades (`IfcUnitAssignment`), contextos de representación geométrica, esquema IFC usado.
- Equivalente conceptual al `<html>` raíz de una página web.

### 3.2 · IfcSite

- Representa **un terreno o parcela**.
- Guarda: coordenadas geográficas (lat/lon/elevación), identificación catastral, norte verdadero.
- Cardinalidad: típicamente 1, pero el esquema permite anidación (campus → recinto → solar). En modelos reales casi siempre hay solo uno.

### 3.3 · IfcBuilding

- Un **edificio físico** dentro del sitio.
- Guarda: elevación de la planta base, tipo (residencial, oficinas…), dirección postal opcional.
- Cardinalidad: 1 IfcSite puede contener **N IfcBuilding** (campus, urbanizaciones, complejos hospitalarios).
- **Regla:** siempre cuelga de un IfcSite, nunca directamente de IfcProject.

### 3.4 · IfcBuildingStorey

- Una **planta horizontal**. Es el "punto de aterrizaje" donde se cuelgan los elementos físicos.
- Guarda: elevación respecto al edificio, nombre ("Sótano -1", "Planta baja", "Cubierta").
- Cardinalidad: N por edificio.
- **Idea clave:** la interfaz entre la jerarquía espacial y los productos físicos.

### 3.5 · IfcSpace

- Un **espacio funcional** (habitación, zona, área de circulación). **Vacío por naturaleza**, no es un elemento construido.
- Guarda: tipo de espacio, volumen, superficie, altura, función.
- Cuelga del **IfcBuildingStorey** (no del Building directamente).
- Diferencia clave: los muros son `IfcWall` (construidos); los espacios son `IfcSpace` (las "burbujas de aire" entre los muros).

### 3.6 · IfcFacility (IFC 4.3+)

Para infraestructura lineal (carreteras, ferrocarril, puentes, puertos), IFC 4.3 introdujo `IfcFacility` con subtipos: `IfcBridge`, `IfcRoad`, `IfcRailway`, `IfcMarineFacility`, etc. Estos sustituyen a `IfcBuilding` en proyectos no-edificación. Relevante para ingeniería de caminos.

---

## 4. Las 5 reglas de oro de la jerarquía espacial

| Regla  | Enunciado                                                                                       |
| ------ | ----------------------------------------------------------------------------------------------- |
| **R1** | `IfcProject` es **único** y obligatorio.                                                        |
| **R2** | Cadena canónica: `IfcProject → IfcSite → IfcBuilding → IfcBuildingStorey → IfcSpace`.           |
| **R3** | Los **elementos físicos** se contienen en un `IfcBuildingStorey` (no en el `IfcBuilding`).      |
| **R4** | Los **espacios** se contienen en un `IfcBuildingStorey` y agrupan elementos por función.        |
| **R5** | Cada producto físico **suele referenciar a un tipo** (`IfcWallType`, etc.) con propiedades comunes. |

---

## 5. El patrón type-instance (capa de tipos)

Uno de los conceptos más potentes del esquema IFC:

- **`IfcWallType/exterior_brick_300mm`** es la **receta** de un muro (capas, espesor, material, propiedades térmicas).
- **`IfcWall/muro_fachada_norte`** es la **instancia física** específica, dibujada en el modelo, que se basa en esa receta.

**Implicaciones prácticas:**

- Múltiples `IfcWall` pueden compartir el **mismo** `IfcWallType` → eficiencia de modelado.
- Si modificas el espesor en el tipo, **todos los muros** instanciados cambian.
- Para preguntar "¿qué material tiene este muro?", no preguntas al `IfcWall`: preguntas a su `IfcWallType` vía la relación `IfcRelDefinesByType`.

**Analogía:** los tipos son las "clases" en programación orientada a objetos, los productos son las "instancias". Patrón clásico que se profundizará en S3.

---

## 6. Decomposición (objetos compuestos)

Algunos elementos son **agregados conceptuales** compuestos por partes físicas:

- `IfcRoof` (cubierta) → puede agregar varios `IfcSlab` (faldones del tejado).
- `IfcStair` (escalera) → agrega `IfcStairFlight`, `IfcStairLanding`.
- `IfcCurtainWall` → agrega `IfcPlate` (paneles) e `IfcMember` (montantes).

La relación se materializa con `IfcRelAggregates`. Permite consultar tanto el todo como las partes.

---

## 7. Clases comodín y señales de calidad

### 7.1 · IfcBuildingElementProxy

Es **el comodín** del esquema: el "no sé qué es esto, pero existe".

- **Uso legítimo:** referencias geométricas no físicas (origen, geo-referencia), elementos auxiliares (capa de arena bajo solera).
- **Uso problemático:** el software exportador no encuentra clase apropiada y mete todo aquí.

**Regla práctica:** si en un IFC ves **>10% de elementos como `IfcBuildingElementProxy`**, sospecha de exportación deficiente. Se materializa en S6 (calidad).

### 7.2 · Otras señales de modelo pobre

- Ausencia total de `IfcSpace` → no hay zonificación funcional.
- Ausencia de tipos (`IfcTypeProduct = 0`) → no hay catálogo, todo modelado ad-hoc.
- Top 5 de clases dominado solo por entidades geométricas primitivas (`IfcCartesianPoint`, `IfcDirection`) en proporciones extremas → modelo "tonto" sin semántica.

---

## 8. Versiones del esquema y compatibilidad

| Versión           | Año aprox. | Estado                  | Usos                              |
| ----------------- | ---------- | ----------------------- | --------------------------------- |
| **IFC 2x3**       | 2006       | Legacy, aún muy común   | Muchos exportadores siguen aquí   |
| **IFC 4.0**       | 2013       | Estable                 | Soporte amplio en software actual |
| **IFC 4.3 (ADD2)**| 2024       | **Actual** · ISO 16739-1:2024 | Edificación + infraestructura lineal |

**Implicaciones prácticas:**

- Un modelo en IFC 2x3 **no tiene** soporte nativo para puentes, carreteras ni ferrocarril.
- Las propiedades semánticas (`Pset_*`) varían entre versiones; **un Pset definido en 4.x puede no existir en 2x3**.
- Comprobar el esquema (`model.schema`) es **el primer paso** al recibir cualquier IFC.

---

## 9. Conexión con el resto del plan

| Concepto de hoy                  | Dónde se profundiza         |
| -------------------------------- | --------------------------- |
| Jerarquía espacial               | **S3** · IFC schema         |
| Type-instance pattern            | **S3** · IFC schema         |
| Recorrido de instancias          | **S4** · IfcOpenShell lectura |
| Geometría y autoría              | **S5** · IfcOpenShell autoría |
| Detección de modelos pobres      | **S6** · Calidad            |
| Exigir reglas (LOIN/IDS)         | **S7** · IDS v1.0           |
| Validación automatizada          | **S8** · ifctester          |
| CI/CD sobre ficheros IFC         | **S9** · CI/CD para BIM     |
| Federación de modelos            | **S11** · CDE OpenBIM       |

---

## 10. Tres ideas para memorizar

1. **IFC = esquema + instancia + implementación.** Los problemas que verás en proyecto suelen vivir en la **implementación**, no en el esquema.
2. **La jerarquía espacial es obligatoria y rígida.** `IfcProject → Site → Building → Storey → Space`. Si falla, todo lo demás falla.
3. **El patrón type-instance es la clave de la eficiencia.** Modelar bien implica usar tipos como catálogo; modelar mal implica duplicar propiedades en cada instancia.

---

## Fuentes citadas

- [buildingSMART · IFC overview](https://www.buildingsmart.org/standards/bsi-standards/industry-foundation-classes/)
- [IFC 4.3.2 documentation](https://ifc43-docs.standards.buildingsmart.org)
- [ISO 16739-1:2024](https://www.iso.org/standard/84123.html)
- [IfcOpenShell · Hello World](https://docs.ifcopenshell.org/ifcopenshell-python/hello_world.html)
- Repo [buildingSMART/Sample-Test-Files](https://github.com/buildingSMART/Sample-Test-Files) utilizado para los 3 IFC del lab.
