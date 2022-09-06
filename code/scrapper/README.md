# Scrapper

Se pueden correr las arañas mediante:

- python3 main.py --spiders_to_run letter --initial_page 2 --final_page 2 --start_date 2022-08-31 --end_date 2022-08-31
- ./main.sh

## Granma

Contiene dos spiders con el objetivo de crawlear el periódico Granma en las secciones de **Edición Impresa** del periódico y en la sección de **Cartas a la Dirección**.

### Edición Impresa

Las urls de la edición impresa está compuesta por la plantilla _https://www.granma.cu/impreso/AÑO-MES-DIA_. En esta página se encuentran las versiones PDF del periódico que se llevaron a la imprenta.

Se extraen de la página todos información acerca de las páginas del día y se descargan los respectivos PDFs.

### Cartas a la Dirección

Las urls de las cartas a la dirección se muestran mediante un sistema de paginado _https://www.granma.cu/archivo?page=PAGE&q=&s=14_. En esta página son recolectadas las direcciones a las cartas que luego son procesadas para extraer la información necesaria.

### Datos

Los datos son guardados en formato json en **granma/data**.
