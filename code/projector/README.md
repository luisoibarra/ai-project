# Projector Package

Se encarga de aplicar los algoritmos de alineación y proyección al corpus.

## Alineadores

Los alineadores son los encargados de dado dos oraciones, una original en lenguaje origen y otra que es la traducción de la original en algún lenguaje objetivo encontrar la alineación de palabras entre ellas. Una alineación de palabras es un enlace entre la palabra de la oración original con la o las palabras que la representan en la oración objetivo. Por ejemplo:

- Oración original: `The blue sky will be dark at night`
- Oración objetivo: `El cielo azul será oscuro en la noche`
- Alineación: `1-1 2-3 3-2 4-4 5-4 6-5 7-6 8-7 8-8`

La alineación como se puede observar es una relación muchos a muchos entre los tokens de las oracion original y objetivo.

### fast_align

TODO

### awesome_align

TODO

## Proyectores

Los proyectores son los encargados de dado dos oraciones, su alineación entre ellas y las etiquetas BIO asociadas
a la oración en lenguage origen, etiquetar la oración en lenguaje objetivo con las etiquetas BIO asociadas. Por ejemplo:

- Oración original: `The blue sky will be dark at night`
- Frase nominal original BIO: `B I I O O O O B`
- Oración objetivo: `El cielo azul será oscuro en la noche`
- Alineación: `1-1 2-3 3-2 4-4 5-4 6-5 7-6 8-7 8-8`
- Frase nominal obetivo BIO: `B I I O O O B I`

### Algoritmo de proyección

TODO

## Traductores

Los traductores son los encargados de traducir las oraciones del lenguage origen al lenguaje objetivo.

### AlgunTraductor?

TODO
