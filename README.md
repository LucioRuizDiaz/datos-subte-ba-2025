# Analizador de Red e Infraestructura - Subte BA 2025

Proyecto bastante vibecodeado en python con el fin de visualizar datos del uso de mi tan querido subte de Buenos Aires el año pasado utilizando los datasets abiertos provistos por el Gobierno de la Ciudad (BA Data).

Armando este proyecto pude aprender a consolidar datasets grandes y ruidosos en un solo archivo, a manejar encodings y a usar Streamlit para armar desarrollo web rápido sin tener que usar CSS.

## Tech Stack

- **Python 3.13**
- **Pandas & PyArrow:** Limpieza, ingeniería de variables temporales y procesamiento por lotes (_chunking_) optimizado mediante formato binario `.parquet`.
- **Streamlit:** Arquitectura de la interfaz web, componentes de filtrado y layouts en cascada.
- **Plotly Express:** Gráficos dinámicos interactivos y mapas vectoriales basados en dispersión por Mapbox (`scatter_mapbox`).

## Estructura del proyecto

- `unificar_datos.py`: Script de ETL. Lee de forma optimizada los 26 archivos CSV mensuales del gobierno, resuelve problemas críticos de codificación (`cp1252`/`latin-1`), remueve comillas accidentales y unifica las variables clave ahorrando un 80% de espacio en memoria RAM.
- `app_subte.py`: Código principal de la aplicación web interactiva de Streamlit.
- `estaciones-accesibles.csv`: Dataset geográfico complementario con coordenadas ($Lat, Long$) e información de ascensores/escaleras mecánicas

## Documentacion

Toda la data que use en este proyecto la saque de [acá](https://data.buenosaires.gob.ar/dataset/subte-viajes-molinetes)

Este apartado detalla el pipeline de datos (ETL) y los criterios de ingeniería de transporte aplicados para transformar los registros de molinetes crudos en métricas geoespaciales.

### 1. Pipeline de Datos (ETL) y Limpieza

El dataset original provisto por _BA Data_ presenta inconsistencias de formato debido al volumen de registros y cambios en los sistemas de carga mensual. El script `unificar_datos.py` resuelve de manera automatizada los siguientes fallos:

- **Tratamiento de Encodings y Caracteres Especiales:** Los archivos alternan su codificación según el período. El motor de ingesta implementa un bucle híbrido de decodificación que prioriza `cp1252` y `latin-1` sobre `utf-8` para salvaguardar tildes y caracteres nativos (como la **Ñ**).
- **Sanitización de Delimitadores de Texto:** El dataset encapsula líneas completas entre comillas dobles (`"FECHA;DESDE;..."`). Para evitar lecturas de índices colapsados en Pandas, se pre-procesa cada archivo como texto plano, removiendo el encapsulado antes de estructurar el DataFrame mediante un búfer de memoria (`io.StringIO`).
- **Filtrado de Registros de Redundancia:** Se eliminan de forma explícita las filas correspondientes a la línea `"Prueba"`, al tratarse de testeos aislados del sistema informático gubernamental que distorsionan las métricas globales.

### 2. Consolidación de Nodos de Combinación

Originalmente, el sistema registra los pasajeros por terminal y molinete de forma aislada, fragmentando estaciones conectadas físicamente. Para reflejar la verdadera carga del entorno urbano, se unificaron las variables en la columna `NODO_CONSOLIDADO` bajo las siguientes reglas:

- **Nodo Obelisco:** Agrupa las estaciones _Carlos Pellegrini (Línea B)_, _9 de Julio (Línea D)_ y _Diagonal Norte (Línea C)_.
- **Nodo Once:** Agrupa _Once (Línea H)_ y _Plaza Miserere (Línea A)_.
- **Nodo Centro Cívico:** Agrupa _Perú (Línea A)_, _Catedral (Línea D)_ y _Bolívar (Línea E)_.
- _Nota:_ El listado completo de los 11 nodos de transferencia cruzada se encuentra parametrizado en la estructura del diccionario `MAPEO_NODOS_COMBINACION`.

## Run Locally

1. Cloná este repositorio:

```bash
   git clone [https://github.com/tu-usuario/subte-ba-2025.git](https://github.com/tu-usuario/subte-ba-2025.git)
   cd subte-ba-2025
```

2. Instalá las dependencias esenciales:

```bash
    pip install streamlit plotly pandas pyarrow
```

3. Lanzá la aplicación en tu navegador:

```bash
    streamlit run app_subte.py
```
