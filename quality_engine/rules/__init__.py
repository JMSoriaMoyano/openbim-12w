"""
quality_engine.rules · Reglas organizadas por dimensión D1-D8.

Una regla = una función pura que recibe (model, params) y devuelve ResultadoCheck.
Las funciones NO acceden directamente al EIR: reciben sus parámetros ya parseados.

Dimensiones según marco S6·L §2:
    d1_modelo         · D1 integridad estructural
    d2_propiedades    · D2 Psets y atributos
    d3_relaciones     · D3 containment, agregación, conexión
    d4_geometria      · D4 representación visual
    d5_unidades       · D5 sistema de unidades
    d6_clasificacion  · D6 sistemas externos
    d7_temporal       · D7 4D planificación (contratista, asbuilt)
    d8_coste          · D8 5D QTO y control de coste (diseño)
"""
