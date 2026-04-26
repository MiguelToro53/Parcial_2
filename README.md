#Parcial2_Info

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
11. [Generación y guardado de gráficas](#11-generación-y-guardado-de-gráficas)
12. [Formato de los archivos de entrada](#12-formato-de-los-archivos-de-entrada)
13. [Cómo agregar nuevos archivos](#13-cómo-agregar-nuevos-archivos)
14. [Errores comunes y soluciones](#14-errores-comunes-y-soluciones)

---

## 1. Descripción general

Este sistema permite explorar, procesar y visualizar de forma interactiva dos tipos de archivos:

- **Archivos CSV del SIATA**: contienen mediciones horarias de calidad del aire en Medellín (PM2.5, PM10, NO, NO₂, NOx, Ozono, CO). El sistema permite ver estadísticas, aplicar operaciones sobre columnas, generar gráficos y analizar la evolución temporal de los contaminantes mediante remuestreo.

- **Archivos MAT de EEG**: contienen señales de electroencefalografías en formato tridimensional `(canales × muestras × épocas)`. El sistema permite explorar la estructura del archivo, sumar canales seleccionados por el usuario y calcular estadísticas por eje sobre la matriz completa.

El sistema se ejecuta completamente desde la consola mediante un menú interactivo. Todos los gráficos generados se guardan automáticamente en carpetas organizadas.

---

## 2. Estructura del proyecto

```
proyecto/
│
├── Validaciones.py       # Todas las clases: Sistema, ArchivoCSV, ArchivoEEG
├── main.py               # Menú interactivo y punto de entrada del programa
│
├── graficos_csv/         # Carpeta creada automáticamente al cargar el primer CSV
│   ├── graficos_pm25_YYYYMMDD_HHMMSS.png
│   └── resample_pm25_YYYYMMDD_HHMMSS.png
│
└── graficos_eeg/         # Carpeta creada automáticamente al cargar el primer EEG
    ├── proceso1_c0-c3-c7_ep0_YYYYMMDD_HHMMSS.png
    └── proceso2_prom_desv_eje2_YYYYMMDD_HHMMSS.png
```

> Las carpetas `graficos_csv/` y `graficos_eeg/` **no necesitan crearse manualmente**. El sistema las genera automáticamente la primera vez que se carga un archivo de cada tipo.

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

El sistema mostrará el menú principal y a partir de ahí todo se controla con el teclado ingresando el número de la opción deseada.

---

## 5. Arquitectura del código

El proyecto sigue una separación clara entre **lógica** e **interfaz**:

```
Validaciones.py                    main.py
───────────────                    ───────
Sistema                            menu_principal()
ArchivoCSV          ◄─── usa ───   submenu_csv()
ArchivoEEG                         submenu_eeg()
                                   utilidades: pedir_entero(),
                                               pedir_opcion(),
                                               seleccionar_objeto()
```

- **`Validaciones.py`** contiene toda la lógica de datos: carga de archivos, cálculos, operaciones y generación de gráficas. No tiene nada de consola ni de menús.
- **`main.py`** contiene únicamente la interfaz de usuario: muestra opciones, pide datos al usuario y llama a los métodos de las clases. No hace ningún cálculo por sí mismo.

Esta separación permite modificar o extender cualquiera de las dos partes sin afectar la otra.

---

## 6. Clase `Sistema`

**Archivo:** `Validaciones.py`  
**Propósito:** actúa como un gestor o registro central. Almacena todos los objetos `ArchivoCSV` y `ArchivoEEG` que se crean durante la ejecución, permitiendo listarlos y buscarlos.

### Atributos

| Atributo | Tipo | Descripción |
|---|---|---|
| `archivos_csv` | `list` | Lista de objetos `ArchivoCSV` registrados |
| `archivos_eeg` | `list` | Lista de objetos `ArchivoEEG` registrados |

### Métodos

#### `agregar_csv(archivo_csv)`
Agrega un objeto `ArchivoCSV` a la lista interna. Verifica que el objeto sea del tipo correcto antes de agregarlo.

#### `agregar_eeg(archivo_eeg)`
Agrega un objeto `ArchivoEEG` a la lista interna. Verifica el tipo del objeto.

#### `listar_archivos()`
Muestra en consola todos los archivos registrados, separados por tipo (CSV y EEG), con numeración.

#### `buscar_csv(nombre)`
Busca un archivo CSV por nombre. La búsqueda es parcial y no distingue mayúsculas de minúsculas. Retorna el objeto si lo encuentra, o `None` si no existe.

#### `buscar_eeg(nombre)`
Igual que `buscar_csv` pero para archivos EEG.

### Ejemplo de uso
```python
from Validaciones import Sistema, ArchivoCSV, ArchivoEEG

sistema = Sistema()
csv = ArchivoCSV("datos/CalAir_VA_2019.csv")
sistema.agregar_csv(csv)
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

- **Subplot 1 – Serie temporal (`plot`):** grafica los valores de la columna en orden de índice. Muestra la variación a lo largo del tiempo sin transformación.
- **Subplot 2 – Boxplot:** muestra la distribución estadística: mediana (línea roja), cuartiles (caja azul), bigotes (valores extremos no atípicos) y puntos fuera de los bigotes (valores atípicos).
- **Subplot 3 – Histograma:** muestra la distribución de frecuencias agrupando los valores en 30 intervalos (bins).

La figura se guarda automáticamente en `graficos_csv/` con el nombre `graficos_{columna}_{timestamp}.png`.

```python
csv.graficar_columna("pm25")
```

---

#### `aplicar_operacion_apply(nombre_columna)`
Crea una nueva columna aplicando `apply()` con una función lambda que calcula la **raíz cuadrada** de cada valor. Si el valor es negativo o nulo, el resultado es `NaN`.

La nueva columna se llama `{columna}_sqrt` y queda guardada en `df`.

```python
csv.aplicar_operacion_apply("pm25")
# Crea columna: pm25_sqrt
```

---

#### `aplicar_operacion_map(nombre_columna)`
Crea una nueva columna aplicando `map()` con una función que **categoriza** cada valor en `'Bajo'`, `'Medio'` o `'Alto'` según los percentiles 33 y 66 de la columna. Los valores nulos se categorizan como `'Sin dato'`.

La nueva columna se llama `{columna}_categoria`.

```python
csv.aplicar_operacion_map("pm25")
# Crea columna: pm25_categoria
```

---

#### `sumar_restar_columnas(columna1, columna2, operacion='suma')`
Suma o resta dos columnas numéricas y crea una nueva columna con el resultado.

| Parámetro | Valor | Resultado |
|---|---|---|
| `operacion` | `'suma'` | Nueva columna: `col1_mas_col2` |
| `operacion` | `'resta'` | Nueva columna: `col1_menos_col2` |

```python
csv.sumar_restar_columnas("pm25", "pm10", "suma")
# Crea columna: pm25_mas_pm10
```

---

#### `convertir_fecha_indice(nombre_columna_fecha='fecha_hora')`
Convierte la columna de fechas a tipo `datetime` y la establece como índice del DataFrame usando `set_index()`. Este paso es **obligatorio** antes de usar `graficar_resample()`.

```python
csv.convertir_fecha_indice("fecha_hora")
```

---

#### `graficar_resample(columna, frecuencias=None)`
Requiere que el índice sea `DatetimeIndex` (haber usado `convertir_fecha_indice` antes).

Realiza un **remuestreo temporal** (`resample().mean()`) en 3 frecuencias y genera una figura con **3 subplots verticales**:

| Frecuencia | Código | Descripción |
|---|---|---|
| Diaria | `'D'` | Promedio de cada día |
| Mensual | `'ME'` | Promedio de cada mes (fin de mes) |
| Trimestral | `'QE'` | Promedio de cada trimestre (fin de trimestre) |

La figura se guarda en `graficos_csv/resample_{columna}_{timestamp}.png`.

```python
csv.graficar_resample("pm25")
```

---

## 8. Clase `ArchivoEEG`

**Archivo:** `Validaciones.py`  
**Propósito:** carga y procesa archivos `.MAT` de electroencefalografías. Mantiene los datos originales intactos y trabaja sobre una copia.

### Estructura esperada del archivo `.MAT`

El archivo debe contener una variable llamada `data` con shape tridimensional:

```
data.shape = (canales, muestras_por_época, épocas)
Ejemplo:     (8,       2000,               138   )
```

- **Canales (eje 0):** electrodos del EEG. En los archivos de prueba hay 8.
- **Muestras por época (eje 1):** puntos temporales dentro de cada época. Con 1000 Hz y 2000 muestras, cada época dura 2 segundos.
- **Épocas (eje 2):** segmentos del registro EEG. En los archivos de prueba hay entre 138 y 180.

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
Se llama automáticamente desde el constructor. Usa `sio.loadmat()` para cargar el archivo, verifica que exista la variable `data` y guarda `data_original` y `data` (copia).

---

#### `mostrar_whosmat()`
Usa `sio.whosmat()` para mostrar todas las variables contenidas en el archivo `.MAT` con su nombre, shape y tipo de dato. Además muestra información detallada de `data`: número de canales, muestras, épocas, frecuencia de muestreo y duración de cada época en segundos.

---

#### `resetear_datos()`
Restaura `data` a una copia de `data_original`.

---

#### `proceso1_sumar_canales(canales, punto_min, punto_max, epoca=0)`

**Propósito:** permite analizar 3 canales individuales en un rango de tiempo definido, sumarlos y comparar visualmente los canales contra su resultado.

**Funcionamiento paso a paso:**

1. **Validación:** verifica que se hayan dado exactamente 3 canales, que todos estén en el rango válido, que `punto_min < punto_max` y que la época exista.

2. **Conversión 3D → 2D:** extrae la época indicada de la matriz original.
   ```
   datos_2d = data[:, :, epoca]
   # shape: (8 canales, 2000 muestras)
   ```

3. **Extracción de canales:** toma los datos de los 3 canales en el rango `[punto_min : punto_max]`.

4. **Suma:** suma los 3 arrays punto a punto con `c1 + c2 + c3`.

5. **Eje temporal:** convierte los índices de muestras a segundos dividiendo por `fs` (1000 Hz).
   ```python
   tiempo = np.arange(punto_min, punto_max) / self.fs
   ```

6. **Gráfico:** genera una figura con 2 subplots verticales:
   - **Subplot superior:** los 3 canales superpuestos con colores distintos y leyenda.
   - **Subplot inferior:** la señal resultante de la suma en color rojo oscuro.

La figura se guarda en `graficos_eeg/proceso1_c{X}-c{Y}-c{Z}_ep{N}_{timestamp}.png`.

```python
eeg.proceso1_sumar_canales([0, 3, 7], punto_min=0, punto_max=500, epoca=0)
```

**Parámetros:**

| Parámetro | Tipo | Descripción |
|---|---|---|
| `canales` | `list[int]` | Lista con exactamente 3 índices de canales |
| `punto_min` | `int` | Muestra de inicio del segmento (incluida) |
| `punto_max` | `int` | Muestra de fin del segmento (excluida) |
| `epoca` | `int` | Índice de la época a analizar (por defecto 0) |

---

#### `proceso2_promedio_desviacion(eje=2)`

**Propósito:** calcula estadísticas descriptivas sobre la señal EEG completa en su forma 3D, sin extraer épocas ni modificar la matriz. Permite observar el comportamiento promedio y la variabilidad de la señal.

**Funcionamiento paso a paso:**

1. **Cálculo sobre la matriz 3D:** aplica `np.mean()` y `np.std()` reduciendo el eje indicado.

   | Eje | Reducción sobre | Shape del resultado |
   |---|---|---|
   | `0` | Canales | `(2000, 138)` |
   | `1` | Muestras/tiempo | `(8, 138)` |
   | `2` *(recomendado)* | Épocas | `(8, 2000)` |

   Con `eje=2` (el más común en EEG): el resultado `(8, 2000)` representa el promedio de cada punto temporal a través de todas las épocas, para cada canal.

2. **Aplanado:** los arrays resultantes se aplanan a 1D con `.flatten()` para poder graficarlos con `stem`.

3. **Gráfico con `stem`:** genera una figura con 2 subplots verticales:
   - **Subplot superior:** stem plot del promedio. Cada línea vertical representa el valor promedio en ese punto.
   - **Subplot inferior:** stem plot de la desviación estándar. Indica cuánto varía la señal alrededor del promedio en ese punto.

4. **Resumen numérico:** imprime en consola el promedio global, la desviación estándar global, el valor máximo y mínimo del promedio.

La figura se guarda en `graficos_eeg/proceso2_prom_desv_eje{N}_{timestamp}.png`.

```python
eeg.proceso2_promedio_desviacion(eje=2)
```

---

## 9. Utilidades del menú (`main.py`)

Son funciones auxiliares que el menú usa internamente para evitar repetir código.

#### `linea(caracter='=', largo=60)`
Imprime una línea decorativa de separación. Usada para dar estructura visual al menú.

#### `titulo(texto)`
Imprime un bloque con el texto enmarcado entre dos líneas. Marca el inicio de cada submenú.

#### `pedir_entero(mensaje, minimo=None, maximo=None)`
Solicita un número entero al usuario con validación completa:
- Si el usuario escribe texto no numérico, vuelve a preguntar.
- Si el número está fuera del rango `[minimo, maximo]`, vuelve a preguntar.
- Solo retorna cuando el valor es válido.

#### `pedir_opcion(opciones_validas, mensaje)`
Solicita una opción de un conjunto de valores permitidos. Si el usuario ingresa algo no listado, vuelve a preguntar. Convierte automáticamente la entrada a minúsculas.

#### `seleccionar_objeto(lista, tipo_nombre)`
Cuando hay varios archivos cargados del mismo tipo, esta función los lista numerados y le pide al usuario que elija uno. Retorna el objeto seleccionado, o `None` si la lista está vacía.

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

## 11. Generación y guardado de gráficas

Todas las gráficas se generan con `matplotlib` y se guardan automáticamente **antes** de mostrarse en pantalla, usando `plt.savefig()` con los siguientes parámetros:

```python
plt.savefig(nombre_archivo, dpi=150, bbox_inches='tight')
```

- **`dpi=150`:** resolución de 150 puntos por pulgada. Produce imágenes de buena calidad sin ser excesivamente pesadas.
- **`bbox_inches='tight'`:** recorta los márgenes blancos sobrantes automáticamente.

El nombre de cada archivo incluye un **timestamp** (`YYYYMMDD_HHMMSS`) para que múltiples ejecuciones no sobreescriban gráficas anteriores.

### Gráficas generadas por funcionalidad

| Método | Archivo generado | Carpeta |
|---|---|---|
| `graficar_columna()` | `graficos_{col}_{ts}.png` | `graficos_csv/` |
| `graficar_resample()` | `resample_{col}_{ts}.png` | `graficos_csv/` |
| `proceso1_sumar_canales()` | `proceso1_c{X}-c{Y}-c{Z}_ep{N}_{ts}.png` | `graficos_eeg/` |
| `proceso2_promedio_desviacion()` | `proceso2_prom_desv_eje{N}_{ts}.png` | `graficos_eeg/` |

---

## 12. Formato de los archivos de entrada

### Archivos CSV (SIATA)

El sistema fue diseñado para archivos con el siguiente formato:

| Columna | Tipo | Descripción |
|---|---|---|
| `fecha_hora` | `str` → `datetime` | Fecha y hora de la medición (formato: `YYYY-MM-DD HH:MM:SS`) |
| `pm25` | `float` | Material particulado 2.5 μm (μg/m³) |
| `pm10` | `float` | Material particulado 10 μm (μg/m³) |
| `no` | `float` | Monóxido de nitrógeno (ppb) |
| `no2` | `float` | Dióxido de nitrógeno (ppb) |
| `nox` | `float` | Óxidos de nitrógeno totales (ppb) |
| `ozono` | `float` | Ozono troposférico (ppb) |
| `co` | `float` | Monóxido de carbono (ppm) |

El archivo `CalAir_VA_2019.csv` contiene **8760 filas** (una por hora durante todo el año 2019).

> El sistema funciona con cualquier CSV que tenga columnas numéricas. La columna `fecha_hora` puede tener otro nombre; simplemente se indica al usar la opción 8 del menú.

### Archivos MAT (EEG)

El archivo `.MAT` debe contener una variable llamada exactamente `data` con shape:
```
(canales, muestras_por_época, épocas)
```

La frecuencia de muestreo está fijada en **1000 Hz** dentro de la clase (`self.fs = 1000`). Si se trabaja con archivos de distinta frecuencia, se debe cambiar ese valor en el constructor.

---

## 13. Cómo agregar nuevos archivos

### Agregar un nuevo CSV desde el menú

1. Ejecutar `python main.py`
2. Elegir opción `1` (Gestión CSV)
3. Elegir opción `1` (Cargar nuevo archivo)
4. Ingresar la ruta completa al archivo, por ejemplo: `C:\datos\nuevo_archivo.csv`
5. Ingresar un nombre descriptivo o presionar Enter para usar el nombre del archivo

### Agregar un nuevo EEG desde el menú

1. Elegir opción `2` (Gestión EEG) en el menú principal
2. Elegir opción `1` (Cargar nuevo archivo)
3. Ingresar la ruta al archivo `.MAT`

### Agregar archivos directamente en código

```python
from Validaciones import Sistema, ArchivoCSV, ArchivoEEG

sistema = Sistema()

# Agregar CSV
csv = ArchivoCSV("ruta/al/archivo.csv", nombre="Mi CSV")
sistema.agregar_csv(csv)

# Agregar EEG
eeg = ArchivoEEG("ruta/al/archivo.mat", nombre="Mi EEG")
sistema.agregar_eeg(eeg)
```

### Agregar soporte para un nuevo tipo de archivo

Para extender el sistema con un tercer tipo de archivo (por ejemplo, `.EDF` de EEG):

1. Crear una nueva clase en `Validaciones.py` siguiendo el mismo patrón:
   - Constructor con `ruta_archivo` y `nombre`
   - Atributos `_original` y copia de trabajo
   - Creación de carpeta de gráficos en `__init__`
   - Métodos de carga privados, información y procesamiento

2. Agregar en la clase `Sistema` dos nuevos métodos: `agregar_nuevo()` y `buscar_nuevo()`.

3. Crear en `main.py` un nuevo submenú `submenu_nuevo()` e integrarlo en `menu_principal()`.

---

## 14. Errores comunes y soluciones

| Error | Causa probable | Solución |
|---|---|---|
| `ModuleNotFoundError: No module named 'scipy'` | scipy no instalado | `pip install scipy` |
| `FileNotFoundError` al cargar archivo | La ruta está mal escrita | Usar ruta absoluta o asegurarse de estar en el directorio correcto |
| `Variable 'data' no encontrada` | El archivo MAT tiene otro nombre de variable | Abrir el archivo con `sio.whosmat()` y ajustar `_cargar_archivo()` |
| `Error: El índice no es datetime` en resample | Se saltó el paso de convertir fechas | Usar primero la opción 8 (convertir_fecha_indice) |
| `Error: La columna no es numérica` | Se eligió una columna de texto | Elegir solo columnas con valores numéricos |
| Las gráficas no se muestran | Backend de matplotlib sin display | En servidores sin pantalla, usar `matplotlib.use('Agg')` al inicio |
| `PermissionError` al guardar gráfico | Sin permisos de escritura en la carpeta | Ejecutar el script desde una carpeta con permisos de escritura |