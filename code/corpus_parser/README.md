# Corpus Parser Package

Útiles para el procesamiento de corpus.

## Parsers

Los parsers permiten la conversión y manejo de corpus. Una de sus principales funciones es el paso de los corpus en su forma original a una represenación estándar más manejable y familiar para los algoritmos a utilizar.

### Conll

Actualmente se soporta el formato .conll. En este se asume que las anotaciones tendrán la forma `"{tok}\t{bio_tag}-{prop_type}-{relation_type}-{relation_distance}\n"` donde sin contar `bio_tag` en adelante las anotaciones son opcionales donde:

- `tok`: La representación textual del token
- `bio_tag`: La etiqueta BIO asociada al token
- `prop_type`: El tipo de componente argumentativa
- `relation_type`: El tipo de relación entre la componente argumentativa que se relaciona
- `realtion_distance`: Distancia en componentes argumentativas de la componente a la que afecta

### Bret

El formato de los corpus bret esperado consta de dos archivos por componente de corpus, el texto original y su anotación en formato .ann. La anotación sigue la regla de:

- componentes argumentativas: `"T{prop_id}\t{prop_type}\t{prop_init}\t{prop_end}\t{prop_text}"`
  - `prop_id`: Id de la componente argumentativa
  - `prop_type`: Tipo de componente argumentativa
  - `prop_init`: Índice inicial de la proposición en el texto original
  - `prop_end`: Índice final de la proposición en el texto original
  - `prop_text`: Texto de la componente
- relaciones: `"{relation_id}\t{relation_type}\tArg1:T{prop_id_source}\tArg2:T{prop_id_target}"`
  - `relation_id`: Id de la relación
  - `relation_type`: Tipo de relación
  - `prop_id_source`: Id de la componente argumentativa fuente
  - `prop_id_target`: Id de la componente argumentativa destino

## Representación de corpus

Dado que los corpus pueden venir de diferentes formas, este paquete se usa para llevarlo a un estandar para
así poder aplicar los algoritmos pertinentes bajo la misma estructura de corpus.

### Representación estandarizada DataFrames

El corpus se representa de manera estándar como un conjunto de DataFrames los cuales guardan la información
relevante.

- componentes_argumentativas: DataFrame que guarda la información relacionada con las componentes argumentativas
  - `prop_id` Proposition ID inside the document
  - `prop_type` Proposition type
  - `prop_init` When the proposition starts in the original text
  - `prop_end` When the proposition ends in the  original text
  - `prop_text` Proposition text

- componentes_no_argumentativas: DataFrame que guarda la información relacionada con las componentes no argumentativas
  - `prop_init` When the proposition starts in the original text
  - `prop_end` When the proposition ends in the   original text
  - `prop_text` Proposition text

- relaciones: DataFrame que guarda la información relacionada con las relaciones
  - `relation_id` Relation ID inside the document
  - `relation_type` Relation type
  - `prop_id_source` Relation's source proposition id
  - `prop_id_target` Relation's target proposition id

### Representación estandarizada archivos

El estándar seleccionado es el formato CONLL con representación textual. Por ejemplo, estos archivos representan una unidad de corpus:

- `archivo1.conll`: Contiene las anotaciones BIO en formato CONLL.
- `archivo1.txt`: Contiene el texto original de las anotaciones.

## TODO

- [ ] Mejorar los tesitng poniendo los test como fixtures.
