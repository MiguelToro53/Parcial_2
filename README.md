# Sistema Explorador de Archivos EEG y SIATA

Documentación completa del proyecto de procesamiento y visualización de archivos `.MAT` (electroencefalografías) y `.CSV` (calidad del aire - SIATA).

---

## Tabla de contenidos

1. [Descripción general](#1-descripción-general)
2. [Estructura del proyecto](#2-estructura-del-proyecto)
3. [Requisitos e instalación](#3-requisitos-e-instalación)
4. [Cómo ejecutar el sistema](#4-cómo-ejecutar-el-sistema)
5. [Arquitectura del código](#5-arquitectura-del-código)
6. [Clase Sistema](#6-clase-sistema)
7. [Clase ArchivoCSV](#7-clase-archivocsv)
8. [Clase ArchivoEEG](#8-clase-archivoeeg)
9. [Utilidades del menú (main.py)](#9-utilidades-del-menú-mainpy)
10. [Menú interactivo](#10-menú-interactivo)
11. [Generación y guardado de gráficas y resultados](#11-generación-y-guardado-de-gráficas-y-resultados)
12. [Persistencia entre sesiones](#12-persistencia-entre-sesiones)
13. [Formato de los archivos de entrada](#13-formato-de-los-archivos-de-entrada)
14. [Cómo agregar nuevos archivos](#14-cómo-agregar-nuevos-archivos)
15. [Errores comunes y soluciones](#15-errores-comunes-y-soluciones)

---

## 1. Descripción general

Este sistema permite explorar, procesar y visualizar de forma interactiva dos tipos de archivos:

- **Archivos CSV del SIATA**: contienen mediciones horarias de calidad del aire en Medellín (PM2.5, PM10, NO, NO2, NOx, Ozono, CO). El sistema permite ver estadísticas, aplicar operaciones sobre columnas, generar gráficos y analizar la evolución temporal de los contaminantes mediante remuestreo.

- **Archivos MAT de EEG**: contienen señales de electroencefalografías en formato tridimensional `(canales x muestras x épocas)`. El sistema permite explorar la estructura del archivo, sumar canales seleccionados por el usuario y calcular estadísticas por eje sobre la matriz completa.

El sistema se ejecuta completamente desde la consola mediante un menú interactivo. Todos los gráficos y resultados de operaciones se guardan automáticamente en carpetas organizadas. Los archivos cargados persisten entre sesiones: al reiniciar el programa, todos los archivos previamente registrados se recuperan automáticamente.

---

## 2. Estructura del proyecto

```
proyecto/
│
├── Validaciones.py           # Todas las clases: Sistema, ArchivoCSV, ArchivoEEG
├── main.py                   # Menú interactivo y punto de entrada del programa
├── sistema_estado.json       # Estado persistente (creado automáticamente)
│
├── graficos_csv/             # Creada automáticamente al cargar el primer CSV
│   ├── graficos_pm25_YYYYMMDD_HHMMSS.png
│   ├── resample_pm25_YYYYMMDD_HHMMSS.png
│   ├── apply_pm25_YYYYMMDD_HHMMSS.csv
│   ├── map_pm25_YYYYMMDD_HHMMSS.csv
│   └── suma_pm25_pm10_YYYYMMDD_HHMMSS.csv
│
└── graficos_eeg/             # Creada automáticamente al cargar el primer EEG
    ├── proceso1_c0-c3-c7_ep0_YYYYMMDD_HHMMSS.png
    └── proceso2_prom_desv_eje2_YYYYMMDD_HHMMSS.png
```

> Las carpetas `graficos_csv/`, `graficos_eeg/` y el archivo `sistema_estado.json` **no necesitan crearse manualmente**. El sistema los genera automáticamente.

Los dos scripts deben estar **en el mismo directorio** para que `main.py` pueda importar `Validaciones.py`.

---

## 3. Requisitos e instalación

### Python
Se requiere **Python 3.8 o superior**. Para verificar la versión instalada:
```bash
python --version
# o
python3 --version
```

### Librerías necesarias

| Librería | Versión mínima | Uso en el proyecto |
|---|---|---|
| `numpy` | 1.21 | Operaciones matriciales con datos EEG |
| `pandas` | 1.3 | Carga y manipulación de archivos CSV |
| `matplotlib` | 3.4 | Generación de todas las gráficas |
| `scipy` | 1.7 | Carga de archivos `.MAT` |

`json` y `os` son parte de la librería estándar de Python y no requieren instalación adicional.

### Instalación de dependencias

Con pip (recomendado):
```bash
pip install numpy pandas matplotlib scipy
```

Con conda:
```bash
conda install numpy pandas matplotlib scipy
```

Verificar que todo quedó instalado correctamente:
```bash
python -c "import numpy, pandas, matplotlib, scipy; print('OK')"
```

---

## 4. Cómo ejecutar el sistema

1. Asegurarse de que `Validaciones.py` y `main.py` están en la misma carpeta.
2. Abrir una terminal en esa carpeta.
3. Ejecutar:

```bash
python main.py
```

El sistema mostrará el menú principal. Si ya hay archivos de sesiones anteriores, los cargará automáticamente antes de mostrar el menú. Todo se controla con el teclado ingresando el número de la opción deseada.

> **Importante:** al cargar archivos, usar siempre **rutas absolutas** (por ejemplo `C:\datos\archivo.csv` en Windows o `/home/usuario/datos/archivo.csv` en Linux/Mac) para garantizar que la persistencia entre sesiones funcione correctamente desde cualquier directorio.

---

## 5. Arquitectura del código

El proyecto sigue una separación clara entre **lógica** e **interfaz**:

```
Validaciones.py                    main.py
───────────────                    ───────
Sistema                            menu_principal()
ArchivoCSV          <─── usa ───   submenu_csv()
ArchivoEEG                         submenu_eeg()
                                   utilidades: pedir_entero(),
                                               pedir_opcion(),
                                               seleccionar_objeto()
```

- **`Validaciones.py`** contiene toda la lógica de datos: carga de archivos, cálculos, operaciones, generación de gráficas y persistencia. No tiene nada de consola ni de menús.
- **`main.py`** contiene únicamente la interfaz de usuario: muestra opciones, pide datos al usuario y llama a los métodos de las clases. No hace ningún cálculo por sí mismo.

Esta separación permite modificar o extender cualquiera de las dos partes sin afectar la otra.

---

## 6. Clase `Sistema`

**Archivo:** `Validaciones.py`  
**Propósito:** actúa como gestor central. Almacena todos los objetos `ArchivoCSV` y `ArchivoEEG` creados durante la ejecución, y gestiona la persistencia entre sesiones mediante un archivo JSON.

### Atributos

| Atributo | Tipo | Descripción |
|---|---|---|
| `archivos_csv` | `list` | Lista de objetos `ArchivoCSV` registrados |
| `archivos_eeg` | `list` | Lista de objetos `ArchivoEEG` registrados |
| `ARCHIVO_ESTADO` | `str` (clase) | Nombre del archivo de persistencia: `sistema_estado.json` |

### Métodos

#### `__init__()`
Constructor. Inicializa las listas vacías y llama automáticamente a `_cargar_estado()` para recuperar archivos de sesiones anteriores.

#### `_guardar_estado()` *(privado)*
Se llama automáticamente cada vez que se agrega un archivo. Escribe en `sistema_estado.json` las rutas y nombres de todos los archivos registrados.

#### `_cargar_estado()` *(privado)*
Se llama automáticamente al iniciar el sistema. Lee `sistema_estado.json` y recarga cada archivo desde disco. Si un archivo fue movido o eliminado, lo omite con una advertencia sin interrumpir el programa.

#### `agregar_csv(archivo_csv)`
Agrega un objeto `ArchivoCSV` a la lista y guarda el estado actualizado en el JSON.

#### `agregar_eeg(archivo_eeg)`
Agrega un objeto `ArchivoEEG` a la lista y guarda el estado actualizado en el JSON.

#### `listar_archivos()`
Muestra en consola todos los archivos registrados, separados por tipo, con numeración.

#### `buscar_csv(nombre)` / `buscar_eeg(nombre)`
Busca un archivo por nombre. La búsqueda es parcial y no distingue mayúsculas de minúsculas. Retorna el objeto si lo encuentra, o `None` si no existe.

### Ejemplo de uso
```python
from Validaciones import Sistema, ArchivoCSV, ArchivoEEG

sistema = Sistema()  # Recupera automáticamente archivos previos
csv = ArchivoCSV("/ruta/absoluta/CalAir_VA_2019.csv")
sistema.agregar_csv(csv)  # Guarda el estado en sistema_estado.json
sistema.listar_archivos()
```

---

## 7. Clase `ArchivoCSV`

**Archivo:** `Validaciones.py`  
**Propósito:** carga y procesa archivos CSV del SIATA. Mantiene el DataFrame original intacto y trabaja sobre una copia, lo que permite resetear los datos en cualquier momento.

### Atributos

| Atributo | Tipo | Descripción |
|---|---|---|
| `ruta_archivo` | `str` | Ruta completa al archivo CSV |
| `nombre` | `str` | Nombre descriptivo del archivo |
| `df_original` | `pd.DataFrame` | DataFrame original sin modificar |
| `df` | `pd.DataFrame` | DataFrame de trabajo (copia) |
| `carpeta_graficos` | `str` | Ruta a `graficos_csv/` |

### Métodos

---

#### `__init__(ruta_archivo, nombre=None)`
Constructor. Carga el archivo CSV, crea la copia de trabajo y la carpeta de gráficos si no existe.

```python
csv = ArchivoCSV("CalAir_VA_2019.csv")
csv = ArchivoCSV("CalAir_VA_2019.csv", nombre="Calidad Aire 2019")
```

---

#### `_cargar_archivo()` *(privado)*
Se llama automáticamente desde el constructor. Usa `pd.read_csv()` para cargar el archivo y crea `df_original` y `df` (copia). No debe llamarse manualmente.

---

#### `mostrar_info()`
Llama a `df.info()` de pandas. Muestra el número de filas, columnas, tipo de dato de cada columna y cantidad de valores no nulos.

---

#### `mostrar_describe()`
Llama a `df.describe()` de pandas. Muestra estadísticas descriptivas de todas las columnas numéricas: conteo, media, desviación estándar, mínimo, cuartiles y máximo.

---

#### `resetear_datos()`
Restaura `df` a una copia fresca de `df_original`. Útil después de haber agregado columnas con `apply`, `map` o suma/resta y querer volver al estado inicial.

---

#### `graficar_columna(nombre_columna)`
Genera y guarda una figura con **3 subplots horizontales** de una columna elegida:

- **Subplot 1 - Serie temporal (`plot`):** grafica los valores de la columna en orden de índice.
- **Subplot 2 - Boxplot:** muestra la distribución estadística: mediana (línea roja), cuartiles (caja azul), bigotes y valores atípicos (puntos negros sobre el bigote).
- **Subplot 3 - Histograma:** muestra la distribución de frecuencias agrupando los valores en 30 intervalos.

Guarda la figura en `graficos_csv/graficos_{columna}_{timestamp}.png`.

```python
csv.graficar_columna("pm25")
```

---

#### `aplicar_operacion_apply(nombre_columna)`
Aplica `apply()` con una función lambda que calcula la **raíz cuadrada** de cada valor. Los valores negativos o nulos producen `NaN`. Crea la columna `{columna}_sqrt` en `df` y guarda el resultado (columna original + columna nueva) en `graficos_csv/apply_{columna}_{timestamp}.csv`.

```python
csv.aplicar_operacion_apply("pm25")
# Crea columna pm25_sqrt y guarda apply_pm25_TIMESTAMP.csv
```

---

#### `aplicar_operacion_map(nombre_columna)`
Aplica `map()` con una función que **categoriza** cada valor en `'Bajo'`, `'Medio'` o `'Alto'` según los percentiles 33 y 66. Los valores nulos se etiquetan como `'Sin dato'`. Crea la columna `{columna}_categoria` en `df` y guarda el resultado en `graficos_csv/map_{columna}_{timestamp}.csv`.

```python
csv.aplicar_operacion_map("pm25")
# Crea columna pm25_categoria y guarda map_pm25_TIMESTAMP.csv
```

---

#### `sumar_restar_columnas(columna1, columna2, operacion='suma')`
Suma o resta dos columnas numéricas y crea una nueva columna con el resultado. Guarda las tres columnas (col1, col2 y resultado) en `graficos_csv/{operacion}_{col1}_{col2}_{timestamp}.csv`.

| `operacion` | Nueva columna | Archivo guardado |
|---|---|---|
| `'suma'` | `col1_mas_col2` | `suma_col1_col2_TIMESTAMP.csv` |
| `'resta'` | `col1_menos_col2` | `resta_col1_col2_TIMESTAMP.csv` |

```python
csv.sumar_restar_columnas("pm25", "pm10", "suma")
```

---

#### `convertir_fecha_indice(nombre_columna_fecha='fecha_hora')`
Convierte la columna de fechas a tipo `datetime` y la establece como índice del DataFrame usando `set_index()`. Este paso es **obligatorio** antes de usar `graficar_resample()`.

```python
csv.convertir_fecha_indice("fecha_hora")
```

---

#### `graficar_resample(columna, frecuencias=None)`
Requiere que el índice sea `DatetimeIndex` (usar `convertir_fecha_indice` antes).

Realiza un **remuestreo temporal** (`resample().mean()`) en 3 frecuencias y genera una figura con **3 subplots verticales**:

| Frecuencia | Código | Descripción |
|---|---|---|
| Diaria | `'D'` | Promedio de cada día |
| Mensual | `'ME'` | Promedio de cada mes (fin de mes) |
| Trimestral | `'QE'` | Promedio de cada trimestre |

Guarda la figura en `graficos_csv/resample_{columna}_{timestamp}.png`.

```python
csv.graficar_resample("pm25")
```

---

## 8. Clase `ArchivoEEG`

**Archivo:** `Validaciones.py`  
**Propósito:** carga y procesa archivos `.MAT` de electroencefalografías. Mantiene los datos originales intactos y trabaja sobre una copia.

### Estructura esperada del archivo `.MAT`

El archivo debe contener una variable llamada exactamente `data` con shape tridimensional:

```
data.shape = (canales, muestras_por_época, épocas)
Ejemplo:     (8,       2000,               138   )
```

- **Canales (eje 0):** electrodos del EEG.
- **Muestras por época (eje 1):** puntos temporales dentro de cada época. Con 1000 Hz y 2000 muestras, cada época dura 2 segundos.
- **Épocas (eje 2):** segmentos del registro EEG.

### Atributos

| Atributo | Tipo | Descripción |
|---|---|---|
| `ruta_archivo` | `str` | Ruta completa al archivo `.MAT` |
| `nombre` | `str` | Nombre descriptivo del archivo |
| `data_original` | `np.ndarray` | Datos originales sin modificar |
| `data` | `np.ndarray` | Datos de trabajo (copia) |
| `fs` | `int` | Frecuencia de muestreo: 1000 Hz |
| `carpeta_graficos` | `str` | Ruta a `graficos_eeg/` |

### Métodos

---

#### `__init__(ruta_archivo, nombre=None)`
Constructor. Carga el archivo `.MAT` usando `scipy.io.loadmat()`, extrae la variable `data`, crea la copia de trabajo y la carpeta de gráficos.

```python
eeg = ArchivoEEG("P004_EP_reposo.mat")
```

---

#### `_cargar_archivo()` *(privado)*
Se llama automáticamente desde el constructor. Carga el archivo, verifica que exista la variable `data` y guarda `data_original` y `data` (copia).

---

#### `mostrar_whosmat()`
Usa `sio.whosmat()` para mostrar todas las variables del archivo `.MAT` con su nombre, shape y tipo de dato. Además muestra información detallada: número de canales, muestras, épocas, frecuencia de muestreo y duración de cada época en segundos.

---

#### `resetear_datos()`
Restaura `data` a una copia de `data_original`.

---

#### `proceso1_sumar_canales(canales, punto_min, punto_max, epoca=0)`

Selecciona 3 canales en un rango de muestras, los suma y genera una figura con 2 subplots:
- **Subplot superior:** los 3 canales individuales superpuestos con colores distintos y leyenda.
- **Subplot inferior:** la señal resultante de sumar los 3 canales.

**Funcionamiento:**
1. Valida canales, rango de puntos y época.
2. Extrae la época indicada convirtiendo la matriz 3D a 2D: `datos_2d = data[:, :, epoca]`.
3. Extrae los 3 canales en el rango `[punto_min:punto_max]`.
4. Suma los 3 arrays punto a punto.
5. Convierte los índices de muestras a segundos: `tiempo = np.arange(punto_min, punto_max) / fs`.

Guarda la figura en `graficos_eeg/proceso1_c{X}-c{Y}-c{Z}_ep{N}_{timestamp}.png`.

```python
eeg.proceso1_sumar_canales([0, 3, 7], punto_min=0, punto_max=500, epoca=0)
```

| Parámetro | Tipo | Descripción |
|---|---|---|
| `canales` | `list[int]` | Lista con exactamente 3 índices de canales |
| `punto_min` | `int` | Muestra de inicio del segmento (incluida) |
| `punto_max` | `int` | Muestra de fin del segmento (excluida) |
| `epoca` | `int` | Índice de la época a analizar (por defecto 0) |

---

#### `proceso2_promedio_desviacion(eje=2)`

Calcula el promedio y la desviación estándar de la matriz 3D a lo largo de un eje y los grafica con stem plots en 2 subplots. La matriz se mantiene en su forma 3D original.

**Funcionamiento:**
1. Aplica `np.mean(data, axis=eje)` y `np.std(data, axis=eje)`.
2. Aplana los resultados a 1D con `.flatten()` para graficarlos con `stem`.
3. Genera 2 subplots verticales: stem del promedio (azul) y stem de la desviación estándar (naranja).
4. Imprime un resumen numérico con promedio global, desviación global, máximo y mínimo.

| Eje | Reducción sobre | Shape del resultado |
|---|---|---|
| `0` | Canales | `(muestras, épocas)` |
| `1` | Muestras/tiempo | `(canales, épocas)` |
| `2` *(recomendado)* | Épocas | `(canales, muestras)` |

Guarda la figura en `graficos_eeg/proceso2_prom_desv_eje{N}_{timestamp}.png`.

```python
eeg.proceso2_promedio_desviacion(eje=2)
```

---

## 9. Utilidades del menú (`main.py`)

Son funciones auxiliares que el menú usa internamente para evitar repetir código. No realizan ningún procesamiento de datos.

#### `linea(caracter='=', largo=60)`
Imprime una línea decorativa de separación visual en el menú.

#### `titulo(texto)`
Imprime un bloque con el texto enmarcado entre dos líneas. Marca el inicio de cada submenú.

#### `pedir_entero(mensaje, minimo=None, maximo=None)`
Solicita un número entero al usuario con validación completa. Si el usuario escribe texto no numérico o un valor fuera del rango `[minimo, maximo]`, vuelve a preguntar hasta recibir un valor válido.

#### `pedir_opcion(opciones_validas, mensaje)`
Solicita una opción de un conjunto de valores permitidos. Si el usuario ingresa algo no listado, vuelve a preguntar. Convierte automáticamente la entrada a minúsculas.

#### `seleccionar_objeto(lista, tipo_nombre)`
Cuando hay varios archivos cargados del mismo tipo, los lista numerados y le pide al usuario que elija uno. Retorna el objeto seleccionado, o `None` si la lista está vacía.

---

## 10. Menú interactivo

Al ejecutar `python main.py` aparece el siguiente árbol de menús:

```
MENÚ PRINCIPAL
├── 1. Gestión CSV
│   ├── 1.  Cargar nuevo archivo CSV
│   ├── 2.  Mostrar info()
│   ├── 3.  Mostrar describe()
│   ├── 4.  Gráficos (plot / boxplot / histograma)
│   ├── 5.  Operación apply() – raíz cuadrada
│   ├── 6.  Operación map() – categorizar
│   ├── 7.  Suma / resta de dos columnas
│   ├── 8.  Convertir columna de fechas a índice
│   ├── 9.  Resample y gráficos temporales
│   ├── 10. Resetear datos
│   └── 0.  Volver
│
├── 2. Gestión EEG
│   ├── 1. Cargar nuevo archivo EEG (.MAT)
│   ├── 2. Mostrar estructura (whosmat)
│   ├── 3. Proceso 1 – Suma de canales
│   ├── 4. Proceso 2 – Promedio y desviación estándar
│   ├── 5. Resetear datos
│   └── 0. Volver
│
├── 3. Listar todos los archivos cargados
└── 0. Salir
```

**Flujo típico para CSV:**
```
1 → cargar archivo → 2 → ver info → 4 → graficar pm25 → 8 → convertir fechas → 9 → resample
```

**Flujo típico para EEG:**
```
1 → cargar archivo → 2 → ver estructura → 3 → proceso 1 → 4 → proceso 2
```

---

## 11. Generación y guardado de gráficas y resultados

### Gráficas (PNG)

Todas las gráficas se generan con `matplotlib` y se guardan automáticamente **antes** de mostrarse en pantalla:

```python
plt.savefig(nombre_archivo, dpi=150, bbox_inches='tight')
```

- **`dpi=150`:** resolución de 150 puntos por pulgada. Buena calidad sin ser excesivamente pesadas.
- **`bbox_inches='tight'`:** recorta los márgenes blancos sobrantes automáticamente.

### Resultados de operaciones (CSV)

Las tres operaciones sobre columnas (apply, map, suma/resta) guardan automáticamente un archivo `.csv` con las columnas involucradas, además de mostrar los resultados en consola.

### Tabla completa de archivos generados

| Método | Tipo | Nombre del archivo | Carpeta |
|---|---|---|---|
| `graficar_columna()` | PNG | `graficos_{col}_{ts}.png` | `graficos_csv/` |
| `graficar_resample()` | PNG | `resample_{col}_{ts}.png` | `graficos_csv/` |
| `aplicar_operacion_apply()` | CSV | `apply_{col}_{ts}.csv` | `graficos_csv/` |
| `aplicar_operacion_map()` | CSV | `map_{col}_{ts}.csv` | `graficos_csv/` |
| `sumar_restar_columnas()` | CSV | `{operacion}_{col1}_{col2}_{ts}.csv` | `graficos_csv/` |
| `proceso1_sumar_canales()` | PNG | `proceso1_c{X}-c{Y}-c{Z}_ep{N}_{ts}.png` | `graficos_eeg/` |
| `proceso2_promedio_desviacion()` | PNG | `proceso2_prom_desv_eje{N}_{ts}.png` | `graficos_eeg/` |

> `{ts}` representa el timestamp en formato `YYYYMMDD_HHMMSS`. Esto garantiza que ningún archivo sobreescriba a uno anterior.

---

## 12. Persistencia entre sesiones

El sistema guarda automáticamente el registro de archivos cargados en `sistema_estado.json`. Esto permite que al detener y volver a ejecutar el programa, todos los archivos previamente cargados se recuperen sin necesidad de cargarlos de nuevo.

### Cómo funciona

Cada vez que se agrega un archivo, `Sistema._guardar_estado()` actualiza el JSON:

```json
{
  "csv": [
    {"ruta": "C:/datos/CalAir_VA_2019.csv", "nombre": "Calidad Aire 2019"}
  ],
  "eeg": [
    {"ruta": "C:/datos/P004_EP_reposo.mat", "nombre": "P004 Reposo"}
  ]
}
```

Al iniciar, `Sistema._cargar_estado()` lee ese JSON y recarga cada archivo. Si algún archivo fue movido o eliminado del disco, se omite con una advertencia y el resto se carga normalmente.

### Mensajes al iniciar

- **Primera vez** (sin JSON): `"Bienvenido. No hay archivos de sesiones anteriores."`
- **Sesiones siguientes**: `"2 archivo(s) recuperado(s) de la sesión anterior. CSV: 1 | EEG: 1"`

### Consideración importante

Las rutas guardadas en el JSON son exactamente las que el usuario ingresó al cargar el archivo. Por eso se recomienda usar siempre **rutas absolutas** al cargar archivos desde el menú, para que funcionen independientemente del directorio desde el que se ejecute el programa.

---

## 13. Formato de los archivos de entrada

### Archivos CSV (SIATA)

El sistema fue diseñado para archivos con el siguiente formato:

| Columna | Tipo | Descripción |
|---|---|---|
| `fecha_hora` | `str` → `datetime` | Fecha y hora de la medición (formato: `YYYY-MM-DD HH:MM:SS`) |
| `pm25` | `float` | Material particulado 2.5 um (ug/m3) |
| `pm10` | `float` | Material particulado 10 um (ug/m3) |
| `no` | `float` | Monóxido de nitrógeno (ppb) |
| `no2` | `float` | Dióxido de nitrógeno (ppb) |
| `nox` | `float` | Óxidos de nitrógeno totales (ppb) |
| `ozono` | `float` | Ozono troposférico (ppb) |
| `co` | `float` | Monóxido de carbono (ppm) |

El archivo `CalAir_VA_2019.csv` contiene **8760 filas** (una por hora durante todo el año 2019).

> El sistema funciona con cualquier CSV que tenga columnas numéricas. La columna de fechas puede tener otro nombre; simplemente se indica al usar la opción 8 del menú.

### Archivos MAT (EEG)

El archivo `.MAT` debe contener una variable llamada exactamente `data` con shape tridimensional:
```
(canales, muestras_por_época, épocas)
```

La frecuencia de muestreo está fijada en **1000 Hz** dentro de la clase (`self.fs = 1000`). Si se trabaja con archivos de distinta frecuencia, se debe cambiar ese valor en el constructor de `ArchivoEEG`.

---

## 14. Cómo agregar nuevos archivos

### Desde el menú (recomendado)

**CSV:**
1. Ejecutar `python main.py`
2. Opción `1` → Gestión CSV → Opción `1` → Cargar nuevo archivo
3. Ingresar la ruta absoluta, por ejemplo: `C:\datos\nuevo_archivo.csv`
4. Ingresar un nombre descriptivo o presionar Enter

**EEG:**
1. Opción `2` → Gestión EEG → Opción `1` → Cargar nuevo archivo
2. Ingresar la ruta absoluta al archivo `.MAT`

### Directamente en código

```python
from Validaciones import Sistema, ArchivoCSV, ArchivoEEG

sistema = Sistema()  # Recupera archivos previos automáticamente

csv = ArchivoCSV("/ruta/absoluta/archivo.csv", nombre="Mi CSV")
sistema.agregar_csv(csv)

eeg = ArchivoEEG("/ruta/absoluta/archivo.mat", nombre="Mi EEG")
sistema.agregar_eeg(eeg)
```

### Agregar soporte para un nuevo tipo de archivo

Para extender el sistema con un tercer tipo de archivo (por ejemplo `.EDF`):

1. Crear una nueva clase en `Validaciones.py` siguiendo el mismo patrón:
   - Constructor con `ruta_archivo` y `nombre`
   - Atributos `_original` y copia de trabajo
   - Creación de carpeta de gráficos en `__init__`
   - Métodos de carga privados, información y procesamiento

2. En la clase `Sistema`: agregar `agregar_nuevo()`, `buscar_nuevo()` y actualizar `_guardar_estado()` y `_cargar_estado()` para incluir el nuevo tipo.

3. En `main.py`: crear `submenu_nuevo()` e integrarlo en `menu_principal()`.

---

## 15. Errores comunes y soluciones

| Error | Causa probable | Solución |
|---|---|---|
| `ModuleNotFoundError: No module named 'scipy'` | scipy no instalado | `pip install scipy` |
| `FileNotFoundError` al cargar archivo | La ruta está mal escrita o es relativa | Usar ruta absoluta completa |
| `Variable 'data' no encontrada` | El archivo MAT tiene otro nombre de variable | Abrir con `sio.whosmat()` y ajustar `_cargar_archivo()` |
| `Error: El índice no es datetime` en resample | Se saltó el paso de convertir fechas | Usar primero la opción 8 (convertir_fecha_indice) |
| `Error: La columna no es numérica` | Se eligió una columna de texto | Elegir solo columnas con valores numéricos |
| Las gráficas no se muestran | Backend de matplotlib sin display | En servidores sin pantalla, usar `matplotlib.use('Agg')` al inicio |
| `PermissionError` al guardar gráfico o CSV | Sin permisos de escritura en la carpeta | Ejecutar desde una carpeta con permisos de escritura |
| Archivo no se recupera al reiniciar | Se usó ruta relativa al cargarlo | Volver a cargarlo usando su ruta absoluta |
| `sistema_estado.json` corrupto | Edición manual incorrecta del JSON | Eliminar el archivo y volver a cargar los archivos desde el menú |