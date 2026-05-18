# S2·L · LOIN en IDS — Cómo IDS materializa el Level of Information Need en formato máquina-legible

> **Sesión:** S2·L · 18/05/2026 · BEP, EIR y plan de información
> **Tema específico:** Conexión LOIN (EN 17412-1) ↔ IDS v1.0 (buildingSMART)
> **Versión:** 1.0 · **Autor:** José M. Soria · **Estado:** Material de estudio

---

## 1. Punto de partida: ¿qué es el LOIN y por qué necesita un soporte máquina-legible?

El **Level of Information Need (LOIN)**, definido en **EN 17412-1:2020** (en adopción internacional como **ISO 7817**), es el marco normativo que sustituye los antiguos esquemas LOD/LOI heredados de PAS 1192. Su propósito es **definir, para cada hito y propósito de uso, qué cantidad y calidad de información debe entregarse — ni más, ni menos**.

La propia norma EN 17412-1 establece una afirmación clave que justifica la existencia de IDS:

> *"The level of information need describes information requirements that can be **human and machine interpretable**."*
> — EN 17412-1:2020, §5

Es decir, el LOIN nace con vocación dual: debe poder ser leído por personas (en el BEP, en el EIR, en plantillas de proyecto) **y** procesado por máquinas (para automatizar la comprobación de cumplimiento). Pero la norma no fija un formato concreto para esa parte máquina-legible — solo define el modelo conceptual. La especificación técnica del formato XML está en **EN 17412-3**, todavía en desarrollo.

En la práctica, la comunidad internacional ha adoptado **IDS (Information Delivery Specification)** de buildingSMART como **el método más ventajoso para la verificación automatizada de los requisitos de información alfanumérica** ([buildingSMART](https://www.buildingsmart.org/methods-to-specify-information-requirements-in-digital-construction-projects/)).

---

## 2. Qué es IDS — definición y posición en el ecosistema OpenBIM

**Information Delivery Specification (IDS)** es un **estándar abierto de buildingSMART** que define un formato XML **interpretable por ordenador** para especificar requisitos de información sobre modelos IFC ([buildingSMART](https://www.buildingsmart.org/standards/bsi-standards/information-delivery-specification-ids/)).

### Datos clave

| Campo | Valor |
|---|---|
| Estado | Estándar oficial de buildingSMART |
| Versión vigente | **v1.0 Final** (publicada 3 junio 2024) |
| Repositorio oficial | https://github.com/buildingSMART/IDS |
| Esquema | `Schema/ids.xsd` (XML Schema Definition) |
| Extensión de archivo | `.ids` |
| Ámbito | Modelos IFC (IFC4, IFC4.3) |

### Posicionamiento

- IDS es **abierto, ligero y estandarizado**: orientado a verificación automatizada y compartible entre herramientas.
- IDS está **limitado a entidades IFC y sus propiedades** — es la pieza que materializa la verificación dentro del entorno OpenBIM.
- IDS **no define geometría detallada** ni mapea procesos de proyecto. Solo cubre la dimensión **alfanumérica** y referencias indirectas a las otras dos dimensiones del LOIN.

Esta limitación es importante: IDS no agota el LOIN, lo **materializa parcialmente** en la dimensión donde la verificación automática aporta más valor.

---

## 3. Las tres dimensiones del LOIN según EN 17412-1

EN 17412-1 descompone los requisitos de información en **tres dimensiones complementarias** ([EN 17412-1:2020 §3.10-3.13](https://cdn.standards.iteh.ai/samples/64241/9badcc548c2d4714833a0770123c337a/SIST-EN-17412-1-2021.pdf)):

### 3.1 Geometrical information (geometría)

> *"Description of detail and extent of information that can be expressed using shape, size, dimension, and location."*

Subdimensiones recogidas por la norma:

- **Detail**: nivel de detalle visual (heredero del antiguo LOD).
- **Dimensionality**: 0D (ubicación), 1D (líneas), 2D (superficies), 3D (volúmenes).
- **Location**: ubicación absoluta (georreferenciación), relativa o por referencia (grids, niveles).
- **Appearance**: representación visual según propósito (clash detection, renderizado, etc.).
- **Parametric behaviour**: geometría explícita, constructiva o paramétrica.

### 3.2 Alphanumerical information (alfanumérica)

> *"Description of detail and extent of information that can be expressed using characters, digits and symbols or tokens such as mathematical symbols and punctuation marks."*

Engloba **identificación, clasificación, propiedades técnicas, parámetros, metadatos**. Es la dimensión predilecta para automatización porque se presta a comparación exacta valor-a-valor.

### 3.3 Documentation (documentación)

Información complementaria que **acompaña** al modelo pero no reside en él: fichas técnicas, certificados, manuales de O&M, garantías, reports de cálculo. La norma EN 17412-1 las trata como entregable separado pero vinculado al objeto BIM.

---

## 4. Cómo IDS materializa el LOIN — la traducción operativa

La conexión conceptual la sintetiza muy bien [Bricsys](https://www.bricsys.com/blog/bridging-the-gap-between-lod-loi-and-the-buildingsmart-ids-with-bricscad-bim):

> *"As a machine-readable document that defines precise information requirements, the IDS serves as structured documentation used to validate BIM content and ensure alignment with LOIN as defined in ISO 7817."*

La traducción dimensión-a-dimensión es la siguiente:

| Dimensión LOIN (EN 17412-1) | Cobertura por IDS v1.0 | Mecanismo en IDS |
|---|---|---|
| **Geometría** | **Parcial e indirecta**. IDS no describe formas. Verifica la **existencia** del objeto y sus **atributos geométricos derivados** (`OverallHeight`, `OverallWidth`, longitud, área, volumen como propiedades cuantitativas). | Facets `Entity` + `Attribute` + `Property` (sobre Psets de cantidades, p.ej. `Qto_WallBaseQuantities`). |
| **Alfanumérica** | **Cobertura completa**. Es el dominio nativo de IDS. | Todos los facets: `Property`, `Classification`, `Material`, `Attribute`. |
| **Documentación** | **Indirecta**. IDS puede exigir que un objeto **referencie** un documento externo (p.ej. via `Pset_ManufacturerTypeInformation`, `ProductReference`), pero el contenido del documento queda fuera de IDS. | Facet `Property` apuntando a propiedades que contienen URIs o IDs de documentos. |

### Mensaje clave

IDS **no sustituye** al LOIN: lo **operacionaliza en la dimensión alfanumérica y en los atributos numéricos derivados de la geometría**. La geometría detallada y la documentación adjunta siguen necesitando otros mecanismos (revisión visual, MVDs, gestión documental en el CDE).

---

## 5. Estructura del XML de IDS — anatomía de un archivo `.ids`

Un archivo IDS sigue esta jerarquía conceptual ([buildingSMART User Manual](https://github.com/buildingSMART/IDS/blob/master/Documentation/UserManual/README.md)):

```
ids (root)
├── info                        ← metadatos del IDS
│   ├── title, copyright, version, description,
│   ├── author, date, purpose, milestone
└── specifications              ← contenedor
    ├── specification 1
    │   ├── applicability       ← "¿a qué elementos aplica?"
    │   │   └── facets[1..n]
    │   └── requirements        ← "¿qué deben cumplir?"
    │       └── facets[1..n]
    ├── specification 2
    │   ├── applicability
    │   └── requirements
    └── ...
```

### Las dos secciones operativas de cada `specification`

| Sección | Función | Pregunta que responde |
|---|---|---|
| **applicability** | Filtro: define el subconjunto de elementos sometidos a verificación | *¿A qué elementos del modelo se aplica esta regla?* |
| **requirements** | Restricciones: define qué deben tener (o no tener) esos elementos | *¿Qué información deben contener para considerarse conformes?* |

Esta separación es la pieza más elegante del estándar: **la misma gramática de facets** sirve para seleccionar el ámbito (applicability) y para imponer las exigencias (requirements). El motor de validación recorre el modelo IFC, identifica los elementos que pasan el filtro y, sobre ellos, comprueba cada requirement.

---

## 6. Los 6 facets de IDS — la gramática de la verificación

Los **facets** son los bloques constructivos del IDS. Hay seis tipos en la v1.0:

### 6.1 `Entity` facet

Filtra o exige un **tipo de entidad IFC**.

- En **applicability**: "esta regla aplica a `IfcWall`".
- En **requirements**: "estos elementos deben ser de tipo `IfcDoor`".
- Soporta también el `predefinedType` (p.ej. `IfcWall.PartitionType`).

**Dimensión LOIN cubierta**: geometría (existencia/tipo) + alfanumérica (clasificación nativa IFC).

### 6.2 `Attribute` facet

Comprueba **atributos nativos de la entidad IFC** (no propiedades de Psets).

- Ejemplos de atributos: `Name`, `Description`, `Tag`, `OverallHeight`, `OverallWidth`.
- Permite comprobar existencia (`IsDefined`) o valor concreto.

**Dimensión LOIN cubierta**: alfanumérica + geometría derivada (alturas, anchuras como atributos directos).

### 6.3 `Classification` facet

Comprueba que el elemento tiene asignada una **clasificación externa** (Uniclass, OmniClass, GuBIMClass, etc.) según la referencia IFC `IfcClassificationReference`.

- Puede exigir un sistema concreto (`Uniclass 2015`) y/o un código concreto (`Ss_25_30_20_30`).

**Dimensión LOIN cubierta**: alfanumérica (taxonomía y referencia normativa).

### 6.4 `Property` facet

El más usado. Comprueba **propiedades dentro de Property Sets** (`Pset_*`) o conjuntos de cantidades (`Qto_*`).

- Parámetros: `propertySet`, `baseName`, `value`, `dataType`, `uri`, `cardinality`, `instructions`.
- Soporta restricciones complejas: enumerations, patterns regex, bounds (rangos numéricos), length restrictions.

**Dimensión LOIN cubierta**: alfanumérica completa + cantidades derivadas de geometría (vía `Qto_*`).

### 6.5 `Material` facet

Comprueba **asignación de material** al elemento (vía `IfcMaterial`, `IfcMaterialLayerSet`, etc.).

- Puede exigir un material concreto (`Concrete C30/37`) o cualquier material definido.

**Dimensión LOIN cubierta**: alfanumérica (especificación constructiva).

### 6.6 `PartOf` facet

Comprueba **relaciones de composición** entre objetos IFC: que un elemento sea parte de otro (agregación, contención, asignación a sistema).

- Útil para exigir que toda `IfcDoor` esté contenida en una `IfcSpace`, o que toda `IfcPipeSegment` pertenezca a un `IfcDistributionSystem`.

**Dimensión LOIN cubierta**: alfanumérica (estructura relacional del modelo).

---

## 7. Restricciones de valor — la potencia expresiva de IDS

Tanto en `applicability` como en `requirements`, los facets que aceptan valores (Attribute, Property, Classification, Material) pueden imponer restricciones más finas que la simple igualdad:

| Restricción | Sintaxis XML (XSD-based) | Caso de uso |
|---|---|---|
| **Valor exacto** | `simpleValue` | "El material debe ser exactamente `Hormigón HA-30`" |
| **Lista cerrada** | `xs:restriction` + `xs:enumeration` | "El tipo de muro debe ser uno de: SOLIDWALL, PARTITIONING, SHEAR" |
| **Patrón** | `xs:restriction` + `xs:pattern` | "El código de clasificación debe seguir la regex `^Ss_25_\d{2}_\d{2}_\d{2}$`" |
| **Rango numérico** | `xs:minInclusive`, `xs:maxInclusive` | "La resistencia al fuego debe estar entre 60 y 180 minutos" |
| **Longitud** | `xs:length`, `xs:minLength`, `xs:maxLength` | "El identificador debe tener al menos 5 caracteres" |
| **Existencia** | `cardinality="required"` / `"optional"` / `"prohibited"` | "La propiedad `FireRating` debe estar definida (pero el valor es libre)" |

Estas restricciones son las que permiten que un IDS exprese verdaderamente un LOIN: no solo *qué información debe estar*, sino *con qué valores admisibles*.

---

## 8. Ejemplo operativo — del LOIN al IDS XML

Supongamos un requisito LOIN extraído de un EIR de proyecto integrador (Hito H3 · Proyecto Ejecutivo):

> *"Todas las puertas exteriores del proyecto deben tener definida su resistencia al fuego (en minutos, entre 30 y 180), clasificadas según Uniclass 2015 (sistema `Pr`), con material principal especificado y vinculadas a un espacio (`IfcSpace`)."*

Este requisito LOIN se materializa así en IDS:

```xml
<ids:specification name="Puertas exteriores · H3 · LOIN ejecutivo"
                   ifcVersion="IFC4">

  <!-- APPLICABILITY: ¿a qué elementos aplica? -->
  <ids:applicability minOccurs="1" maxOccurs="unbounded">
    <ids:entity>
      <ids:name><ids:simpleValue>IFCDOOR</ids:simpleValue></ids:name>
    </ids:entity>
    <ids:property dataType="IfcBoolean">
      <ids:propertySet><ids:simpleValue>Pset_DoorCommon</ids:simpleValue></ids:propertySet>
      <ids:baseName><ids:simpleValue>IsExternal</ids:simpleValue></ids:baseName>
      <ids:value><ids:simpleValue>TRUE</ids:simpleValue></ids:value>
    </ids:property>
  </ids:applicability>

  <!-- REQUIREMENTS: ¿qué deben cumplir? -->
  <ids:requirements>

    <!-- (1) Resistencia al fuego como propiedad con rango numérico -->
    <ids:property dataType="IfcTimeMeasure" cardinality="required">
      <ids:propertySet><ids:simpleValue>Pset_DoorCommon</ids:simpleValue></ids:propertySet>
      <ids:baseName><ids:simpleValue>FireRating</ids:simpleValue></ids:baseName>
      <ids:value>
        <xs:restriction base="xs:double">
          <xs:minInclusive value="30"/>
          <xs:maxInclusive value="180"/>
        </xs:restriction>
      </ids:value>
    </ids:property>

    <!-- (2) Clasificación Uniclass 2015 con patrón regex -->
    <ids:classification cardinality="required">
      <ids:system><ids:simpleValue>Uniclass 2015</ids:simpleValue></ids:system>
      <ids:value>
        <xs:restriction base="xs:string">
          <xs:pattern value="^Pr_\d{2}_\d{2}_\d{2}_\d{2}$"/>
        </xs:restriction>
      </ids:value>
    </ids:classification>

    <!-- (3) Material definido (cualquier valor admisible) -->
    <ids:material cardinality="required"/>

    <!-- (4) Relación: la puerta debe pertenecer a un IfcSpace -->
    <ids:partOf relation="IFCRELCONTAINEDINSPATIALSTRUCTURE" cardinality="required">
      <ids:entity>
        <ids:name><ids:simpleValue>IFCSPACE</ids:simpleValue></ids:name>
      </ids:entity>
    </ids:partOf>

  </ids:requirements>
</ids:specification>
```

### Lectura del ejemplo

- **Applicability** combina dos facets (`Entity` + `Property`) para acotar el ámbito: solo puertas exteriores.
- **Requirements** usa **cuatro facets distintos** para cubrir las tres dimensiones del LOIN:
  - Geometría derivada (FireRating como dato cuantitativo).
  - Alfanumérica (clasificación, material).
  - Estructura relacional (PartOf).
- La documentación adjunta (la ficha técnica de cada puerta) NO se incluye aquí: queda fuera del alcance de IDS, gestionada en el CDE.

---

## 9. Flujo de trabajo IDS — autor, validador y reporte

El flujo operativo del estándar es ([Plannerly](https://plannerly.com/information-delivery-specification-ids-the-complete-guide-to-automating-bim-validation/)):

```
1. Cliente / appointing party
   └── Identifica requisitos de información (LOIN por hito)
            ↓
2. Information manager
   └── Redacta el IDS (.ids XML) — manual o con editor (BIMcollab, Plannerly, ifctester)
            ↓
3. Lead appointed party
   └── Distribuye IDS a las disciplinas vía CDE
            ↓
4. Disciplinas (appointed parties)
   └── Autocomprueban sus IFC contra el IDS antes de publicar
            ↓
5. QA/QC BIM (information manager)
   └── Validación oficial: IFC + IDS → reporte de cumplimiento
            ↓
6. Publicación en CDE solo si pasa la validación
```

### Posición del IDS en el ciclo ISO 19650

El IDS se concibe en la actividad **5.2 (Invitation to tender)** como anexo del EIR, se refina en el **BEP** durante 5.3-5.4, y se aplica operativamente en **5.6 (Information production)** y **5.7 (Information delivery)**. Es la pieza que **convierte el EIR de declarativo a verificable**.

---

## 10. Herramientas que soportan IDS v1.0

| Herramienta | Capacidad | Tipo |
|---|---|---|
| **ifctester** (IfcOpenShell) | Autoría + validación + reporting (Console, JSON, ODS, HTML, BCF) | OSS · Python · CLI |
| **BIMcollab Zoom / ONE** | Editor visual + validación | Comercial |
| **Plannerly** | Editor web colaborativo | Comercial |
| **Solibri** | Validación integrada en ruleset checking | Comercial |
| **usBIM.IDSeditor** (ACCA) | Editor IDS gratuito | Freemium |
| **IDS Editor (Trimble)** | Editor + validación | Comercial |

Para el plan formativo, **ifctester** es la elección coherente: ya está instalado en el entorno `openbim`, es open source, integrable en CI/CD (S9) y autoría programática desde Python.

---

## 11. Limitaciones de IDS v1.0 — lo que NO cubre

Para no construir expectativas falsas:

1. **No describe geometría detallada**: no puede exigir un nivel concreto de detalle visual ni una topología específica. Para eso siguen siendo necesarios MVDs y revisión visual.
2. **No mapea procesos**: no sustituye al MIDP/TIDP — no dice *cuándo* se entrega la información, solo *qué* debe contener.
3. **No es contractual por sí solo**: IDS describe requisitos técnicos, pero su exigibilidad nace del EIR/BEP que lo invocan.
4. **Solo IFC**: no es aplicable fuera del ecosistema OpenBIM/IFC.
5. **Documentación externa indirecta**: solo puede exigir referencias a documentos, no validar su contenido.

Para los requisitos geométricos detallados, EN 17412-3 (en desarrollo) prevé un mecanismo complementario más completo.

---

## 12. Conclusión — el papel de IDS en el plan de información

**IDS v1.0 es, hoy, la materialización operativa de facto del LOIN en su dimensión alfanumérica y en los atributos numéricos derivados de la geometría.** Convierte un requisito que tradicionalmente se expresaba en lenguaje natural dentro de un EIR/BEP (y por tanto, sujeto a interpretación) en una regla XML inequívoca, verificable por máquina, distribuible entre disciplinas y auditable en cada publicación del CDE.

Para el flujo de NEXUM como *appointing party*:

- El **EIR (E2)** declara *qué información se necesita* y enuncia el LOIN por hito en lenguaje humano.
- El **BEP (E2)** describe *cómo* se va a entregar y validar.
- El **IDS (objetivo de S7)** es el puente máquina-legible que cierra el ciclo: el mismo requisito, esta vez ejecutable por `ifctester` y reportable en cada hito.

Ese es el motivo por el que S2 y S7 son las dos sesiones más interconectadas del plan formativo: una redacta el requisito, la otra lo automatiza.

---

## Fuentes

1. [Information Delivery Specification (IDS) · buildingSMART International](https://www.buildingsmart.org/standards/bsi-standards/information-delivery-specification-ids/) — página oficial del estándar.
2. [What is Information Delivery Specification (IDS) · buildingSMART](https://www.buildingsmart.org/what-is-information-delivery-specification-ids/) — alcance y posicionamiento.
3. [Methods to specify information requirements in digital construction projects · buildingSMART](https://www.buildingsmart.org/methods-to-specify-information-requirements-in-digital-construction-projects/) — comparativa IDS vs IDM vs LOIN.
4. [buildingSMART/IDS · GitHub](https://github.com/buildingSMART/IDS) — repositorio oficial, esquema XSD y user manual.
5. [User Manual (development branch) · buildingSMART/IDS](https://github.com/buildingSMART/IDS/blob/master/Documentation/UserManual/README.md) — estructura applicability/requirements y los 6 facets.
6. [IfcTester · IfcOpenShell 0.8.5 documentation](https://docs.ifcopenshell.org/ifctester.html) — autoría programática y validación en Python.
7. [EN 17412-1:2020 (muestra oficial iTeh Standards)](https://cdn.standards.iteh.ai/samples/64241/9badcc548c2d4714833a0770123c337a/SIST-EN-17412-1-2021.pdf) — definiciones de geometrical/alphanumerical information y dimensiones del LOIN.
8. [Bridging the Gap Between LOD, LOI, and the buildingSMART IDS · Bricsys](https://www.bricsys.com/blog/bridging-the-gap-between-lod-loi-and-the-buildingsmart-ids-with-bricscad-bim) — relación LOD/LOI/LOIN/IDS bajo ISO 7817.
9. [Information Delivery Specification (IDS): The Complete Guide to Automating BIM Validation · Plannerly](https://plannerly.com/information-delivery-specification-ids-the-complete-guide-to-automating-bim-validation/) — flujo de autoría y distribución.
10. [Creating an IDS · BIMcollab Help Center](https://helpcenter.bimcollab.com/en/articles/327351-creating-an-ids-information-delivery-specification) — operadores de restricción (Is, IsDefined, OneOf, Contains, Starts with, Ends with, Regex pattern).
