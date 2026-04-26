"""
Archivo que contiene todas las clases para el procesamiento de archivos
CSV (SIATA - Calidad del Aire) y MAT (EEG - Electroencefalografías).
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scipy.io as sio
from datetime import datetime
import os
import json


# CLASE SISTEMA - Gestor de objetos creados

class Sistema:
    """
    Clase que gestiona y almacena todos los objetos de archivos creados
    (tanto CSV como MAT). Permite búsqueda y listado de objetos.
    
    """
    ARCHIVO_ESTADO = "sistema_estado.json"

    def __init__(self):
        """
        Constructor de la clase Sistema.
        """
        self.archivos_csv = []  # Lista de objetos ArchivoCSV
        self.archivos_eeg = []  # Lista de objetos ArchivoEEG
        self._cargar_estado()   # Carga el estado anterior

    def _guardar_estado(self):
        estado = {
            "csv": [{"ruta": a.ruta_archivo, "nombre": a.nombre}
                    for a in self.archivos_csv],
            "eeg": [{"ruta": a.ruta_archivo, "nombre": a.nombre}
                    for a in self.archivos_eeg]
        }
        with open(self.ARCHIVO_ESTADO, "w", encoding="utf-8") as f:
            json.dump(estado, f, indent=2, ensure_ascii=False)

    def _cargar_estado(self):
        if not os.path.exists(self.ARCHIVO_ESTADO):
            return
        try:
            with open(self.ARCHIVO_ESTADO, "r", encoding="utf-8") as f:
                estado = json.load(f)
            csv_recuperados = 0
            for entrada in estado.get("csv", []):
                if os.path.exists(entrada["ruta"]):
                    try:
                        obj = ArchivoCSV(entrada["ruta"], entrada["nombre"])
                        self.archivos_csv.append(obj)
                        csv_recuperados += 1
                    except Exception as e:
                        print(f" No se pudo recargar '{entrada['nombre']}': {e}")
                else:
                    print(f" Archivo no encontrado, se omite: {entrada['ruta']}")
            eeg_recuperados = 0
            for entrada in estado.get("eeg", []):
                if os.path.exists(entrada["ruta"]):
                    try:
                        obj = ArchivoEEG(entrada["ruta"], entrada["nombre"])
                        self.archivos_eeg.append(obj)
                        eeg_recuperados += 1
                    except Exception as e:
                        print(f" No se pudo recargar '{entrada['nombre']}': {e}")
                else:
                    print(f" Archivo no encontrado, se omite: {entrada['ruta']}")
            total = csv_recuperados + eeg_recuperados
            if total > 0:
                print(f"\n {total} archivo(s) recuperado(s) de la sesión anterior.")
                print(f"   CSV: {csv_recuperados} | EEG: {eeg_recuperados}")
        except Exception as e:
            print(f" Error al leer el estado guardado: {e}")
        
    def agregar_csv(self, archivo_csv):
        """
        Agrega un objeto ArchivoCSV al sistema.
        
        Parámetros:
        archivo_csv : ArchivoCSV
        Objeto de tipo ArchivoCSV a agregar
        """
        if isinstance(archivo_csv, ArchivoCSV):
            self.archivos_csv.append(archivo_csv)
            self._guardar_estado()  # Guardar estado después de agregar
            print(f" Archivo CSV '{archivo_csv.nombre}' agregado al sistema")
        else:
            print(" Error: El objeto no es de tipo ArchivoCSV")
    
    def agregar_eeg(self, archivo_eeg):
        """
        Agrega un objeto ArchivoEEG al sistema.
        
        Parámetros:
        archivo_eeg : ArchivoEEG
        Objeto de tipo ArchivoEEG a agregar
        """
        if isinstance(archivo_eeg, ArchivoEEG):
            self.archivos_eeg.append(archivo_eeg)
            self._guardar_estado()  # Guardar estado después de agregar
            print(f" Archivo EEG '{archivo_eeg.nombre}' agregado al sistema")
        else:
            print(" Error: El objeto no es de tipo ArchivoEEG")
    
    def listar_archivos(self):

        print("ARCHIVOS ALMACENADOS EN EL SISTEMA")
        
        print(f"\n Archivos CSV (SIATA): {len(self.archivos_csv)}")
        for i, archivo in enumerate(self.archivos_csv, 1):
            print(f"  {i}. {archivo.nombre}")
        
        print(f"\n Archivos EEG: {len(self.archivos_eeg)}")
        for i, archivo in enumerate(self.archivos_eeg, 1):
            print(f"  {i}. {archivo.nombre}")
        
    
    def buscar_csv(self, nombre):
        """
        Busca un archivo CSV por nombre.
        
        Parámetros:
        
        nombre : str
        Nombre del archivo a buscar
            
        Retorna:
        
        ArchivoCSV o None
        El objeto encontrado o None si no existe
        """
        for archivo in self.archivos_csv:
            if nombre.lower() in archivo.nombre.lower():
                return archivo
        return None
    
    def buscar_eeg(self, nombre):
        """
        Busca un archivo EEG por nombre.
        
        Parámetros:
       
        nombre : str
        Nombre del archivo a buscar
            
        Retorna:
        
        ArchivoEEG o None
        El objeto encontrado o None si no existe
        """
        for archivo in self.archivos_eeg:
            if nombre.lower() in archivo.nombre.lower():
                return archivo
        return None



# CLASE ARCHIVOCSV - Manipulación de archivos CSV del SIATA


class ArchivoCSV:
    """
    Clase para manipular archivos CSV del SIATA.
    Permite cargar, visualizar información, graficar y realizar operaciones
    sobre los datos.
    """
    
    def __init__(self, ruta_archivo, nombre=None):
        """
        Constructor de la clase ArchivoCSV.
        
        Parámetros:
        
        ruta_archivo : str
            Ruta completa al archivo CSV
        nombre : str, opcional
            Nombre descriptivo del archivo (si no se provee, usa el nombre del archivo)
        """
        self.ruta_archivo = ruta_archivo
        self.nombre = nombre if nombre else os.path.basename(ruta_archivo)
        self.df_original = None  # DataFrame original 
        self.df = None  # DataFrame de trabajo (copia)
        self.carpeta_graficos = "graficos_csv"  # Carpeta para guardar gráficos
        
        # Crear carpeta de gráficos si no existe
        if not os.path.exists(self.carpeta_graficos):
            os.makedirs(self.carpeta_graficos)
        
        # Cargar el archivo
        self._cargar_archivo()
    
    def _cargar_archivo(self):
        """
        Método privado para cargar el archivo CSV.
        Carga el archivo original y crea una copia de trabajo.
        """
        try:
            # Cargar archivo original (se mantiene intacto)
            self.df_original = pd.read_csv(self.ruta_archivo)
            
            # Crear copia de trabajo
            self.df = self.df_original.copy()
            
            print(f" Archivo CSV cargado exitosamente: {self.nombre}")
            print(f"  Dimensiones: {self.df.shape[0]} filas x {self.df.shape[1]} columnas")
            
        except Exception as e:
            print(f" Error al cargar el archivo: {str(e)}")
            raise
    
    def mostrar_info(self):
        """
        Muestra información básica del DataFrame usando info().
        """
        print(f"INFORMACIÓN BÁSICA - {self.nombre}")
        self.df.info()

    
    def mostrar_describe(self):
        """
        Muestra estadísticas descriptivas del DataFrame usando describe().
        """
        
        print(f"ESTADÍSTICAS DESCRIPTIVAS - {self.nombre}") 
        print(self.df.describe())

    
    def resetear_datos(self):
        """
        Restaura el DataFrame de trabajo a su estado original.
        """
        self.df = self.df_original.copy()
        print(" Datos restaurados al estado original")
    
    def graficar_columna(self, nombre_columna):
        """
        Crea 3 gráficos (plot, boxplot, histograma) de una columna específica.
        Los gráficos se muestran en subplots y se guardan automáticamente.
        
        Parámetros:
    
        nombre_columna : str
            Nombre de la columna a graficar
        """
        # Validar que la columna exista
        if nombre_columna not in self.df.columns:
            print(f"✗ Error: La columna '{nombre_columna}' no existe")
            print(f"  Columnas disponibles: {list(self.df.columns)}")
            return
        
        # Validar que la columna sea numérica
        if not pd.api.types.is_numeric_dtype(self.df[nombre_columna]):
            print(f" Error: La columna '{nombre_columna}' no es numérica")
            return
        
        # Crear figura con 3 subplots
        fig, axes = plt.subplots(1, 3, figsize=(15, 4))
        fig.suptitle(f'Análisis de {nombre_columna}', fontsize=14, fontweight='bold')
        
        # 1. Plot (línea temporal)
        axes[0].plot(self.df[nombre_columna], linewidth=0.8, color='steelblue')
        axes[0].set_title('Serie Temporal')
        axes[0].set_xlabel('Índice')
        axes[0].set_ylabel(nombre_columna)
        axes[0].grid(True, alpha=0.3)
        
        # 2. Boxplot
        axes[1].boxplot(self.df[nombre_columna].dropna(), vert=True, patch_artist=True,
                       boxprops=dict(facecolor='lightblue', color='steelblue'),
                       whiskerprops=dict(color='steelblue'),
                       capprops=dict(color='steelblue'),
                       medianprops=dict(color='red', linewidth=2))
        axes[1].set_title('Diagrama de Caja')
        axes[1].set_ylabel(nombre_columna)
        axes[1].grid(True, alpha=0.3, axis='y')
        
        # 3. Histograma
        axes[2].hist(self.df[nombre_columna].dropna(), bins=30, color='skyblue', 
                    edgecolor='steelblue', alpha=0.7)
        axes[2].set_title('Histograma')
        axes[2].set_xlabel(nombre_columna)
        axes[2].set_ylabel('Frecuencia')
        axes[2].grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        
        # Guardar gráfico

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_archivo = f"{self.carpeta_graficos}/graficos_{nombre_columna}_{timestamp}.png"
        plt.savefig(nombre_archivo, dpi=150, bbox_inches='tight')
        print(f" Gráfico guardado: {nombre_archivo}")
        
        plt.show()
    
    def aplicar_operacion_apply(self, nombre_columna):
        """
        Aplica una operación usando apply() sobre una columna.
        Ejemplo: Convertir valores a su raíz cuadrada.
        
        Parámetros:

        nombre_columna : str
            Nombre de la columna sobre la cual aplicar la operación
        """
        if nombre_columna not in self.df.columns:
            print(f" Error: La columna '{nombre_columna}' no existe")
            return
        
        if not pd.api.types.is_numeric_dtype(self.df[nombre_columna]):
            print(f" Error: La columna '{nombre_columna}' no es numérica")
            return
        
        # Aplicar raíz cuadrada usando apply 
        nueva_columna = f"{nombre_columna}_sqrt"
        self.df[nueva_columna] = self.df[nombre_columna].apply(lambda x: np.sqrt(x) if x >= 0 else np.nan)
        
        print(f" Operación apply() completada:")
        print(f"  Nueva columna '{nueva_columna}' creada con raíz cuadrada de '{nombre_columna}'")
        print(f"\nPrimeros 5 valores:")
        print(self.df[[nombre_columna, nueva_columna]].head())

        # Guardar resultado en CSV
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_archivo = f"graficos_csv/apply_{nombre_columna}_{timestamp}.csv"
        self.df[[nombre_columna, nueva_columna]].to_csv(nombre_archivo, index=True)
        print(f"\n Resultado guardado en: {nombre_archivo}")
    
    def aplicar_operacion_map(self, nombre_columna):
        """
        Aplica una operación usando map() sobre una columna.
        Ejemplo: Clasificar valores en categorías (Bajo, Medio, Alto).
        
        Parámetros:
        
        nombre_columna : str
            Nombre de la columna sobre la cual aplicar la operación
        """
        if nombre_columna not in self.df.columns:
            print(f" Error: La columna '{nombre_columna}' no existe")
            return
        
        if not pd.api.types.is_numeric_dtype(self.df[nombre_columna]):
            print(f" Error: La columna '{nombre_columna}' no es numérica")
            return
        
        # Calcular percentiles para categorización
        p33 = self.df[nombre_columna].quantile(0.33)
        p66 = self.df[nombre_columna].quantile(0.66)
        
        # Función de categorización
        def categorizar(valor):
            if pd.isna(valor):
                return 'Sin dato'
            elif valor < p33:
                return 'Bajo'
            elif valor < p66:
                return 'Medio'
            else:
                return 'Alto'
        
        # Aplicar map
        nueva_columna = f"{nombre_columna}_categoria"
        self.df[nueva_columna] = self.df[nombre_columna].map(categorizar)
        
        print(f" Operación map() completada:")
        print(f"  Nueva columna '{nueva_columna}' creada con categorías")
        print(f"  Rangos: Bajo < {p33:.2f} | Medio < {p66:.2f} | Alto >= {p66:.2f}")
        print(f"\nDistribución de categorías:")
        print(self.df[nueva_columna].value_counts())

        # Guardar resultado en CSV
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_archivo = f"graficos_csv/map_{nombre_columna}_{timestamp}.csv"
        self.df[[nombre_columna, nueva_columna]].to_csv(nombre_archivo, index=True)
        print(f"\n Resultado guardado en: {nombre_archivo}")
    
    def sumar_restar_columnas(self, columna1, columna2, operacion='suma'):
        """
        Suma o resta dos columnas y crea una nueva columna con el resultado.
        
        Parámetros:
        columna1 : str
            Nombre de la primera columna
        columna2 : str
            Nombre de la segunda columna
        operacion : str
            'suma' o 'resta' (por defecto 'suma')
        """
        # Validar columnas
        if columna1 not in self.df.columns:
            print(f" Error: La columna '{columna1}' no existe")
            return
        if columna2 not in self.df.columns:
            print(f" Error: La columna '{columna2}' no existe")
            return
        
        if not pd.api.types.is_numeric_dtype(self.df[columna1]):
            print(f" Error: La columna '{columna1}' no es numérica")
            return
        if not pd.api.types.is_numeric_dtype(self.df[columna2]):
            print(f" Error: La columna '{columna2}' no es numérica")
            return
        
        # Realizar operación
        if operacion.lower() == 'suma':
            nueva_columna = f"{columna1}_mas_{columna2}"
            self.df[nueva_columna] = self.df[columna1] + self.df[columna2]
            simbolo = '+'
        elif operacion.lower() == 'resta':
            nueva_columna = f"{columna1}_menos_{columna2}"
            self.df[nueva_columna] = self.df[columna1] - self.df[columna2]
            simbolo = '-'
        else:
            print(" Error: Operación no válida. Use 'suma' o 'resta'")
            return
        
        print(f" Operación {operacion} completada:")
        print(f"  Nueva columna '{nueva_columna}' = {columna1} {simbolo} {columna2}")
        print(f"\nPrimeros 5 valores:")
        print(self.df[[columna1, columna2, nueva_columna]].head())

        # Guardar resultado en CSV
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_archivo = f"graficos_csv/{operacion}_{columna1}_{columna2}_{timestamp}.csv"
        self.df[[columna1, columna2, nueva_columna]].to_csv(nombre_archivo, index=True)
        print(f"\n Resultado guardado en: {nombre_archivo}")

    def convertir_fecha_indice(self, nombre_columna_fecha='fecha_hora'):
            """
            Convierte la columna de fechas en índice del DataFrame.
            
            Parámetros:
            
            nombre_columna_fecha : str
                Nombre de la columna que contiene las fechas (por defecto 'fecha_hora')
            """
            if nombre_columna_fecha not in self.df.columns:
                print(f" Error: La columna '{nombre_columna_fecha}' no existe")
                return
            
            # Convertir a datetime y establecer como índice
            self.df[nombre_columna_fecha] = pd.to_datetime(self.df[nombre_columna_fecha])
            self.df.set_index(nombre_columna_fecha, inplace=True)
            
            print(f" Columna '{nombre_columna_fecha}' convertida a índice")
            print(f"  Rango de fechas: {self.df.index.min()} a {self.df.index.max()}")
            
    def graficar_resample(self, columna, frecuencias=['D', 'ME', 'QE']):
            """
            Realiza resample de los datos y grafica en diferentes frecuencias temporales.
            Requiere que el índice sea de tipo datetime.
            
            Parámetros:
            columna : str
                Nombre de la columna a graficar
            frecuencias : list
                Lista de frecuencias para resample (por defecto ['D', 'ME', 'QE'])
                D = Días, ME = Meses (Month End), QE = Trimestres (Quarter End)
            """
            # Validar que el índice sea datetime
            if not isinstance(self.df.index, pd.DatetimeIndex):
                print(" Error: El índice debe ser de tipo datetime")
                print("  Use primero el método convertir_fecha_indice()")
                return
            
            # Validar columna
            if columna not in self.df.columns:
                print(f" Error: La columna '{columna}' no existe")
                return
            
            if not pd.api.types.is_numeric_dtype(self.df[columna]):
                print(f" Error: La columna '{columna}' no es numérica")
                return
            
            # Diccionario de nombres de frecuencias
            nombres_freq = {
                'D': 'Diario',
                'ME': 'Mensual',
                'QE': 'Trimestral',
                'M': 'Mensual',  # Para compatibilidad hacia atrás
                'Q': 'Trimestral'  # Para compatibilidad hacia atrás
            } 
    # Crear figura con subplots
            n_freq = len(frecuencias)
            fig, axes = plt.subplots(n_freq, 1, figsize=(12, 4*n_freq))
            
            # Si solo hay una frecuencia, axes no es array
            if n_freq == 1:
                axes = [axes]
            
            fig.suptitle(f'Resample de {columna} en diferentes frecuencias', 
                        fontsize=14, fontweight='bold')
            
            # Graficar para cada frecuencia
            for i, freq in enumerate(frecuencias):
                # Realizar resample (promedio)
                datos_resample = self.df[columna].resample(freq).mean()
                
                # Graficar
                axes[i].plot(datos_resample.index, datos_resample.values, 
                            marker='o', linewidth=2, markersize=4, color='steelblue')
                axes[i].set_title(f'Resample {nombres_freq.get(freq, freq)}')
                axes[i].set_xlabel('Fecha')
                axes[i].set_ylabel(f'{columna} (promedio)')
                axes[i].grid(True, alpha=0.3)
                axes[i].tick_params(axis='x', rotation=45)
            
            plt.tight_layout()
            
            # Guardar gráfico
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nombre_archivo = f"{self.carpeta_graficos}/resample_{columna}_{timestamp}.png"
            plt.savefig(nombre_archivo, dpi=150, bbox_inches='tight')
            print(f" Gráfico de resample guardado: {nombre_archivo}")
            
            plt.show()



# CLASE ARCHIVOEEG - Manipulación de archivos .MAT de EEG

class ArchivoEEG:
    """
    Clase para manipular archivos .MAT de electroencefalografías (EEG).
    Permite cargar, visualizar estructura y procesar señales de EEG.
    """
    
    def __init__(self, ruta_archivo, nombre=None):
        """
        Constructor de la clase ArchivoEEG.
        
        Parámetros:
        
        ruta_archivo : str
            Ruta completa al archivo .MAT
        nombre : str, opcional
            Nombre descriptivo del archivo (si no se provee, usa el nombre del archivo)
        """
        self.ruta_archivo = ruta_archivo
        self.nombre = nombre if nombre else os.path.basename(ruta_archivo)
        self.data_original = None  # Datos originales (nunca se modifican)
        self.data = None  # Datos de trabajo (copia)
        self.fs = 1000  # Frecuencia de muestreo en Hz
        self.carpeta_graficos = "graficos_eeg"  # Carpeta para guardar gráficos
        
        # Crear carpeta de gráficos si no existe
        if not os.path.exists(self.carpeta_graficos):
            os.makedirs(self.carpeta_graficos)
        
        # Cargar el archivo
        self._cargar_archivo()

    def _cargar_archivo(self):
        """
        Método privado para cargar el archivo .MAT.
        Carga el archivo original y crea una copia de trabajo.
        """
        try:
            # Cargar archivo .MAT
            mat_contents = sio.loadmat(self.ruta_archivo)
            
            # Extraer la variable 'data' (estructura esperada)
            if 'data' in mat_contents:
                self.data_original = mat_contents['data']
                self.data = self.data_original.copy()
                
                print(f" Archivo EEG cargado exitosamente: {self.nombre}")
                print(f"  Dimensiones: {self.data.shape}")
                print(f"  Formato: (canales={self.data.shape[0]}, " +
                      f"muestras={self.data.shape[1]}, épocas={self.data.shape[2]})")
            else:
                print(" Error: No se encontró la variable 'data' en el archivo")
                raise ValueError("Variable 'data' no encontrada")
                
        except Exception as e:
            print(f" Error al cargar el archivo: {str(e)}")
            raise
    
    def mostrar_whosmat(self):
        """
        Muestra las claves y estructura del archivo .MAT usando whosmat().
        """
        print(f"ESTRUCTURA DEL ARCHIVO - {self.nombre}")
       
        
        # Usar whosmat para mostrar información
        contents = sio.whosmat(self.ruta_archivo)
        
        print("\n Variables en el archivo:")
        for variable_name, shape, dtype in contents:
            print(f"  • Variable: {variable_name}")
            print(f"    Shape: {shape}")
            print(f"    Tipo: {dtype}")
        
        print("\n Información detallada de 'data':")
        print(f"  • Canales: {self.data.shape[0]}")
        print(f"  • Muestras por época: {self.data.shape[1]}")
        print(f"  • Número de épocas: {self.data.shape[2]}")
        print(f"  • Frecuencia de muestreo: {self.fs} Hz")
        print(f"  • Duración por época: {self.data.shape[1]/self.fs} segundos")
       
    
    def resetear_datos(self):
        """
        Restaura los datos de trabajo a su estado original.
        """
        self.data = self.data_original.copy()
        print(" Datos restaurados al estado original")
    
    def proceso1_sumar_canales(self, canales, punto_min, punto_max, epoca=0):
            """
            Proceso 1: Selecciona 3 canales en un rango de puntos, los suma
            y genera un gráfico con 2 subplots:
            - Subplot superior : los 3 canales individuales.
            - Subplot inferior : la suma de los 3 canales.
    
            La matriz se trabaja en 2D extrayendo la época indicada
            (shape resultante: canales x muestras).
    
            Parámetros:
            
            canales : list[int]
                Lista con exactamente 3 índices de canales (ej. [0, 3, 7]).
            punto_min : int
                Punto inicial del rango de muestras (incluido).
            punto_max : int
                Punto final del rango de muestras (excluido).
            epoca : int
                Índice de la época a analizar (por defecto 0).
            """
            #  Validaciones
            if len(canales) != 3:
                print(" Error: Debe seleccionar exactamente 3 canales.")
                return
    
            for canal in canales:
                if canal < 0 or canal >= self.data.shape[0]:
                    print(f" Error: Canal {canal} fuera de rango "
                        f"(válido: 0–{self.data.shape[0]-1}).")
                    return
    
            if punto_min < 0 or punto_max > self.data.shape[1]:
                print(f" Error: Rango de puntos inválido "
                    f"(válido: 0–{self.data.shape[1]}).")
                return
    
            if punto_min >= punto_max:
                print(" Error: punto_min debe ser menor que punto_max.")
                return
    
            if epoca < 0 or epoca >= self.data.shape[2]:
                print(f" Error: Época {epoca} fuera de rango "
                    f"(válido: 0–{self.data.shape[2]-1}).")
                return
    
            # Procesamiento 
            # Convertir 3D → 2D para la época seleccionada
            datos_2d = self.data[:, :, epoca]   # shape: (canales, muestras)
    
            c1 = datos_2d[canales[0], punto_min:punto_max]
            c2 = datos_2d[canales[1], punto_min:punto_max]
            c3 = datos_2d[canales[2], punto_min:punto_max]
    
            suma = c1 + c2 + c3
    
            # Eje temporal en segundos
            tiempo = np.arange(punto_min, punto_max) / self.fs
    
            # Gráficos 
            fig, axes = plt.subplots(2, 1, figsize=(12, 8))
            fig.suptitle(
                f'Proceso 1 – Suma de Canales {canales} | {self.nombre} | Época {epoca}',
                fontsize=13, fontweight='bold'
            )
    
            # Subplot 1: canales individuales
            colores = ['steelblue', 'darkorange', 'seagreen']
            for idx, (datos_canal, color) in enumerate(zip([c1, c2, c3], colores)):
                axes[0].plot(tiempo, datos_canal, label=f'Canal {canales[idx]}',
                            linewidth=1, alpha=0.85, color=color)
            axes[0].set_title('Canales Individuales')
            axes[0].set_xlabel('Tiempo (s)')
            axes[0].set_ylabel('Amplitud (μV)')
            axes[0].legend(loc='upper right')
            axes[0].grid(True, alpha=0.3)
    
            # Subplot 2: suma de canales
            axes[1].plot(tiempo, suma, linewidth=1.5, color='darkred')
            axes[1].set_title(
                f'Suma: Canal {canales[0]} + Canal {canales[1]} + Canal {canales[2]}'
            )
            axes[1].set_xlabel('Tiempo (s)')
            axes[1].set_ylabel('Amplitud (μV)')
            axes[1].grid(True, alpha=0.3)
    
            plt.tight_layout()
    
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nombre_archivo = (f"{self.carpeta_graficos}/proceso1_"
                            f"c{canales[0]}-c{canales[1]}-c{canales[2]}_"
                            f"ep{epoca}_{timestamp}.png")
            plt.savefig(nombre_archivo, dpi=150, bbox_inches='tight')
            print(f" Gráfico guardado: {nombre_archivo}")
            plt.show()
    
            print(f"\n Resumen del procesamiento:")
            print(f"   Canales seleccionados : {canales}")
            print(f"   Rango de muestras     : {punto_min}–{punto_max}")
            print(f"   Número de muestras    : {punto_max - punto_min}")
            print(f"   Duración analizada    : {(punto_max - punto_min) / self.fs:.3f} s")
            print(f"   Época analizada       : {epoca}")  

    def proceso2_promedio_desviacion(self, eje=2):
        """
        Proceso 2: Calcula el promedio y la desviación estándar de la matriz
        3D a lo largo de un eje y los grafica usando stem plots en 2 subplots.
 
        La matriz se mantiene en su forma 3D original; numpy reduce el eje
        indicado y produce arrays 2D que se aplanan para la visualización.
 
        Ejes disponibles:
          - eje=0 : reducción sobre canales   → resultado shape (muestras, épocas)
          - eje=1 : reducción sobre muestras  → resultado shape (canales, épocas)
          - eje=2 : reducción sobre épocas    → resultado shape (canales, muestras)
 
        Parámetros:
       
        eje : int
            Eje sobre el cual calcular (0, 1 o 2). Por defecto 2 (épocas).
        """
        # Validación 
        if eje not in [0, 1, 2]:
            print(" Error: El eje debe ser 0, 1 o 2.")
            return
 
        nombres_eje = {
            0: 'canales (eje 0)',
            1: 'muestras/tiempo (eje 1)',
            2: 'épocas (eje 2)'
        }
 
        print(f"\n Calculando promedio y desviación estándar sobre {nombres_eje[eje]}...")

        # Cálculo sobre la matriz 3D 
        promedio = np.mean(self.data, axis=eje)   # shape resultante varía según eje
        desviacion = np.std(self.data, axis=eje)
 
        # Aplanar para graficar con stem (1D)
        prom_flat = promedio.flatten()
        desv_flat = desviacion.flatten()
        indices = np.arange(len(prom_flat))
 
        # Gráficos con stem 
        fig, axes = plt.subplots(2, 1, figsize=(14, 9))
        fig.suptitle(
            f'Proceso 2 – Promedio y Desviación Estándar\n'
            f'{self.nombre} | Reducción sobre {nombres_eje[eje]}',
            fontsize=13, fontweight='bold'
        )
 
        # Subplot 1: Promedio (stem)
        markerline, stemlines, baseline = axes[0].stem(
            indices, prom_flat, linefmt='steelblue', markerfmt='C0o',
            basefmt='k-'
        )
        plt.setp(stemlines, linewidth=0.6, alpha=0.7)
        plt.setp(markerline, markersize=3)
        axes[0].set_title(f'Promedio a lo largo de {nombres_eje[eje]}')
        axes[0].set_xlabel('Índice (aplanado)')
        axes[0].set_ylabel('Amplitud media (μV)')
        axes[0].grid(True, alpha=0.25)
 
        # Subplot 2: Desviación estándar (stem)
        markerline2, stemlines2, baseline2 = axes[1].stem(
            indices, desv_flat, linefmt='darkorange', markerfmt='C1o',
            basefmt='k-'
        )
        plt.setp(stemlines2, linewidth=0.6, alpha=0.7)
        plt.setp(markerline2, markersize=3)
        axes[1].set_title(f'Desviación Estándar a lo largo de {nombres_eje[eje]}')
        axes[1].set_xlabel('Índice (aplanado)')
        axes[1].set_ylabel('Desviación estándar (μV)')
        axes[1].grid(True, alpha=0.25)
 
        plt.tight_layout()
 
        # Guardar gráfico
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_archivo = (f"{self.carpeta_graficos}/proceso2_"
                          f"prom_desv_eje{eje}_{timestamp}.png")
        plt.savefig(nombre_archivo, dpi=150, bbox_inches='tight')
        print(f" Gráfico guardado: {nombre_archivo}")
        plt.show()
 
        # Resumen numérico
        print(f"\n Resumen estadístico:")
        print(f"   Shape original de 'data'  : {self.data.shape}")
        print(f"   Eje de reducción          : {eje} ({nombres_eje[eje]})")
        print(f"   Shape del resultado       : {promedio.shape}")
        print(f"   Promedio global           : {prom_flat.mean():.4f} μV")
        print(f"   Desv. estándar global     : {desv_flat.mean():.4f} μV")
        print(f"   Valor máx. del promedio   : {prom_flat.max():.4f} μV")
        print(f"   Valor mín. del promedio   : {prom_flat.min():.4f} μV")