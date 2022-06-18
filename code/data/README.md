# Data

Carpeta en donde se incluirán los corpus para su trabajo más organizado. No es obligatoria su inclusión en esta carpeta.

## Organización

Se piensa una estructura jerárquica basada en los diferentes estados de los documentos y los diferentes corpus a procesar. En el repositorio se encuentra un ejemplo de la propuesta hecha. Esta consiste en dividir el corpus en 5 partes:

1. corpus: Corpus inicial sin procesar.
2. parsed_to_conll: Corpus procesado en el [formato estándar](corpus_parser/README.md) de archivo propuesto.
3. sentence_alignment: Oraciones del corpus alineadas en lenguaje fuente y lenguaje objetivo.
4. bidirectional_alignment: Alineaciones de las oraciones alineadas.
5. projection: Corpus en formato estándar con las anotaciones proyectadas en el lenguaje objetivo.

Dentro de cada una de estas divisiones se encontrará un nombre que se le quiera dar al corpus, en el ejemplo se nombra **testing** al nombre del corpus con que se trabaja.
