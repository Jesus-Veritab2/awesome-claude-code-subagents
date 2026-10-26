# Recon map: Presupuestador de sistemas de placa de yeso (web)

Referencia: Selector de Sistemas Pladur (https://selector-de-sistemas.pladur.com/)
Alcance: leer las partidas de una obra desde PDF, asociar cada partida a un
sistema (tabique, trasdosado, techo), calcular materiales y precio, y guardar
cada sistema calculado para reutilizarlo.
Para: uso interno de la empresa del usuario (no se vende).
Fecha: 2026-10-26

> Nota: no es un clon del selector. El usuario lo considera obsoleto (hay que
> elegir las partidas una a una). Se toma de él solo el **conocimiento de
> cálculo** (consumos por m² de cada sistema) y el **modelo de precio**
> (tarifa − descuento). El flujo es nuevo.

## Fuentes

| # | fuente | URL | notas |
| --- | --- | --- | --- |
| 1 | Selector de Sistemas Pladur | https://selector-de-sistemas.pladur.com/ | **No observado.** La red del entorno bloquea pladur.com. Sin pantallas propias. |
| 2 | Prensa del sector | https://www.alimarket.es/construccion/noticia/423670/pladur-presenta-su-modelo-de-co-creacion-de-soluciones-constructivas | El selector filtra por prestaciones/normativa y genera presupuesto con bases de precios (requiere registro). |
| 3 | Manual técnico Pladur | https://media.pladur.com/pi99466/original/262312996/manual-tecnico-es-pladur.pdf | Fuente de las recetas de consumo. Pendiente de que el usuario lo suba (bloqueado aquí). |
| 4 | Guía de sistemas Pladur (jul. 2025) | https://documentacion.generadordeprecios.info/documentaciontecnica/pladur/pladur_guia.pdf | Clasificación: tabiques de separación/distribución, trasdosados, techos, especiales. |
| 5 | PDF de obra del usuario | `PARTIDAS_PLADUR.pdf` (subido, 7 págs.) | Documento real a presupuestar. Es **imagen escaneada** (Word → Print to PDF), sin capa de texto. |
| 6 | Modelo de precio del usuario | conversación | Precio = tarifa del selector − descuento: **48 % placas, 39 % resto**. |

## Core loop

Subir el PDF de partidas de una obra → la app reconoce cada partida, reutiliza
el cálculo si ya existe o lo calcula y lo guarda → presupuesto completo.

## Lo que dice el PDF de obra (fuente 5)

16 partidas. El número de la derecha es la **medición** (cantidad), no el precio.

| código | ud | descripción corta | tipo | medición | ¿sistema Pladur? |
| --- | --- | --- | --- | --- | --- |
| B2010-T123.0980 | m2 | Fachada casetones cubierta F11 (bloque hormigón + trasdosado placa cemento 12,5 + LR 80 + lámina FPO) | mixta | 364,37 | parcial |
| C1010-T131.2500 | m2 | Tab. 175/400 (2x12.5A+125+2x12.5A) c/aisl. h≤6,20 DR04 | tabique | 133,49 | sí |
| C1010-T131.2940 | m2 | Tab. 175/400 (2x12.5A+125+2x12.5H1) c/aisl. h≤6,20 DR03 | tabique | 192,82 | sí |
| C1010-T131.3040 | m2 | Tab. 120/400 (2x12.5H1+70+2x12.5H1) c/aisl. h≤4,25 DR05 | tabique | 63,27 | sí |
| C1010-T131.3500 | m2 | Tab. 150/400 (2x12.5H1+100+2x12.5H1) c/aisl. h≤5,25 DR01 | tabique | 10,06 | sí |
| C1010-T131.3600 | m2 | Tab. 175/400 (2x12.5H1+125+2x12.5H1) c/aisl. h≤6,20 DR02 | tabique | 28,56 | sí |
| C1010-T131.4501 | m2 | Trasd. autoport. 150/400 (100)(2x25DF) c/aisl. EI-60 LI06 | trasdosado | 634,78 | sí |
| C1010-T131.7000 | m2 | Trasd. autoport. 73/600 (48)(2x12.5A) c/aisl. LI03 | trasdosado | 589,99 | sí |
| C1010-T131.7100 | m2 | Trasd. autoport. 73/600 (48)(2x12.5H1) c/aisl. LI01 | trasdosado | 289,08 | sí |
| C1010-T131.7500 | m2 | Trasd. autoport. 95/400 (70)(2x12.5H1) c/aisl. LI02 | trasdosado | 283,78 | sí |
| C1010-T131.7800 | m2 | Trasd. autoport. 115/400 (90)(2x12.5A) c/aisl. LI04 | trasdosado | 1.614,44 | sí |
| C1010-T136.3200 | m2 | Barrera fónica lana de roca 80 mm aluminio MF01 | aislamiento | 49,87 | no (otro fabricante) |
| C1070-T168.4440 | m2 | F.T. continuo H1 15 mm, descuelgue 1,50–2,50 m, tipo 10 | techo | 130,95 | sí |
| C1070-T168.4500 | m2 | F.T. continuo A 15 mm, descuelgue 1,50–2,50 m, tipo 11 | techo | 78,05 | sí |
| C1070-T168.4900 | m | Tabica en falso techo placa 15 mm, h≤100 cm | tabica | 16,03 | sí |
| C1070-T168.4950 | ud | Registro 600x600 aluminio + placa H1 15 | accesorio | 9,00 | sí (accesorio) |

Observaciones que condicionan el diseño:

- **El código no sirve como clave.** Los códigos (C1010-T131.2500) son del
  proyecto/cliente, no de Pladur. Lo que identifica el sistema es la
  **composición**: tipo, placas por cara, perfil, separación, aislamiento.
- **Las caras pueden ser distintas** (DR03: A en una cara, H1 en la otra).
- La descripción trae todos los datos técnicos: perfil y espesor de chapa
  (montante 125x50 0,6 mm, canal 125x40 0,6 mm), separación (400/600), lana
  mineral (70 kg/m³, 40/60/80 mm), altura máxima.
- **Incoherencia en el original**: la partida tipo 10 dice "1,50<D<2,50 m" en
  el título y "entre 1,50 m y 2,00 m" en el texto. La app debe avisar de este
  tipo de conflictos, no elegir uno en silencio.
- Textos "Documentación LEED" y garantías: ruido para el cálculo, se ignoran.

## Pantallas (de la app nueva)

Las del selector no se han podido observar. Estas son las de la app propuesta.

| ID | pantalla | cómo se llega | propósito | componentes clave | estados |
| --- | --- | --- | --- | --- | --- |
| S01 | Obras | inicio | lista de obras/presupuestos | tabla, botón nueva obra | vacío, con datos |
| S02 | Subir PDF | S01 → nueva obra | cargar el PDF de partidas | zona de arrastre, progreso | vacío, leyendo, error de lectura |
| S03 | Revisión de partidas | tras S02 | ver cada partida detectada y su estado: **en biblioteca** / **nueva, calculada** / **necesita revisión** / **no es sistema (precio manual)** | tabla, chips de estado, panel lateral | todo reconocido, con dudas, con conflictos |
| S04 | Ficha de sistema | S03 o S05 | composición normalizada + receta de materiales por m² | formulario, tabla de consumos | nuevo, guardado, conflicto |
| S05 | Biblioteca de sistemas | menú | todos los sistemas ya calculados | buscador, filtros por tipo | vacío, con datos |
| S06 | Materiales y tarifa | menú | precio de tarifa de cada material + familia de descuento (placas 48 %, resto 39 %) | tabla editable, importar tarifa | vacío, con datos, precio caducado |
| S07 | Presupuesto | S03 → generar | partidas × medición × precio, totales, márgenes | tabla, totales, ajustes | borrador, cerrado |
| S08 | Exportar | S07 | PDF/Excel del presupuesto y lista de materiales para pedido | vista previa | — |
| S09 | Ajustes | menú | datos de empresa, logo, mano de obra, margen, IVA | formulario | — |

## Flujos

```
F01 Presupuestar una obra desde su PDF
    S01 -> S02 -> S03 -> S07 -> S08
    happy path: 4 clics (nueva obra, subir, generar, exportar) si todo está en biblioteca
    edge: PDF escaneado (OCR), partida ambigua, partida no Pladur (F11, MF01),
          incoherencia título/texto, unidades m2 / m / ud

F02 Partida nueva que no está en la biblioteca
    S03 -> S04 (la app propone la receta; el usuario la revisa) -> guardar -> S03
    edge: caras distintas, altura fuera de rango del sistema, material sin precio

F03 Actualizar la tarifa (cambio de precios anual)
    S06 -> importar tarifa -> todos los sistemas se recalculan solos
    edge: material desaparecido o renombrado en la nueva tarifa
```

Referencia a batir: en el selector hay que buscar y añadir cada partida a mano
(16 partidas = 16 búsquedas como mínimo). Aquí: 1 subida.

## Componentes

| componente | variantes | estados | usado en |
| --- | --- | --- | --- |
| Botón | primario, secundario, peligro | normal, deshabilitado, cargando | todas |
| Zona de subida | — | vacía, arrastrando, leyendo, error | S02 |
| Tabla de partidas | — | fila ok, fila con aviso, fila en error | S03, S07 |
| Chip de estado | en biblioteca, nueva, revisar, manual | — | S03 |
| Tabla de consumos | editable, solo lectura | — | S04 |
| Campo numérico con unidad | €, %, m, m², ud | válido, error | S04, S06, S09 |
| Totales | — | — | S07 |

## Modelo de datos inferido

```
Material      id, ref_fabricante, nombre, unidad (m2|m|ud|kg|l),
              familia_descuento (placa | resto), precio_tarifa, fecha_tarifa
              evidencia: descripciones de partidas (placas A/H1/DF/N, montantes,
              canales, lana mineral, tornillos, cinta, pasta); modelo de precio del usuario
              confianza: alta

Sistema       id, tipo (tabique | trasdosado | techo | tabica | accesorio),
              clave_composicion (única), placas_cara_1[], placas_cara_2[],
              perfil (ancho x ala, espesor), separacion_mm, aislamiento (tipo, densidad, espesor),
              altura_max_m, descuelgue_min/max, resistencia_fuego, unidad
              evidencia: PDF de obra, 16 partidas
              confianza: alta

LineaReceta   sistema_id, material_id, consumo_por_unidad
              evidencia: manual técnico Pladur (pendiente)
              confianza: media hasta tener el manual

Obra          id, nombre, cliente, fecha, pdf_original
Partida       id, obra_id, codigo_cliente, texto_original, unidad, medicion,
              sistema_id (nullable), precio_manual (nullable), avisos[]
              evidencia: PDF de obra
              confianza: alta

Ajustes       descuento_placas (48 %), descuento_resto (39 %), mano_de_obra_por_tipo,
              margen, iva
              evidencia: conversación; mano de obra = pendiente
              confianza: media
```

Relaciones: Sistema 1-n LineaReceta n-1 Material; Obra 1-n Partida n-1 Sistema.

**Decisión clave: se guarda la receta, no el precio.** El precio de cada
sistema se calcula en el momento (consumos × tarifa × (1 − descuento)). Así,
cuando cambie la tarifa, toda la biblioteca se actualiza sola (F03).

## Matriz de funcionalidades

Ver `features.csv`. Must: 12, should: 7, could: 4, skip: 2.

## Fuera de alcance

- **Copiar la base de datos del selector** (sacar todos los precios entrando
  con la cuenta): extracción masiva, probablemente contraria a sus
  condiciones de uso. Los precios salen de la **tarifa oficial** de Pladur
  (o de la de tu proveedor) y las recetas del **manual técnico**.
- El catálogo de ensayos y certificados de Pladur (acústica, fuego): se
  guarda solo la clasificación que diga la partida (p. ej. EI-60).

## Tamaño

Pantallas 9, flujos 3, entidades 6. Partes difíciles:
1. Leer PDF escaneados y convertir cada descripción en una composición
   normalizada (OCR + extracción con IA + revisión humana).
2. Recetas de consumo correctas por sistema (perfiles según altura,
   separación, tornillería, pasta, cinta, % de mermas): validar con el manual.
3. Partidas mixtas o de otros fabricantes (F11, MF01): precio manual o
   receta propia.

Tamaño: **M** (unas semanas).

## Pendiente del usuario

- Manual técnico Pladur en PDF (recetas).
- Tarifa de precios Pladur en PDF o Excel (precio base al que aplicar 48 % / 39 %).
- ¿El precio del selector incluye mano de obra? Si no, precio de mano de obra por m² de cada tipo.
- Confirmar que la columna de la derecha del PDF es la medición.
