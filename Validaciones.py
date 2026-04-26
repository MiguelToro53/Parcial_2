"""
Archivo que contiene todas las clases para el procesamiento de archivos
CSV (SIATA - Calidad del Aire) y MAT (EEG - Electroencefalografías).
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
#import scipy.io as sio
from datetime import datetime
import os


# CLASE SISTEMA - Gestor de objetos creados

class Sistema:
    """
    Clase que gestiona y almacena todos los objetos de archivos creados
    (tanto CSV como MAT). Permite búsqueda y listado de objetos.
    """
    
    def __init__(self):
        """
        Constructor de la clase Sistema.
        """
        self.archivos_csv = []  # Lista de objetos ArchivoCSV
        self.archivos_eeg = []  # Lista de objetos ArchivoEEG
        
    def agregar_csv(self, archivo_csv):
        """
        Agrega un objeto ArchivoCSV al sistema.
        
        Parámetros:
        archivo_csv : ArchivoCSV
        Objeto de tipo ArchivoCSV a agregar
        """
        if isinstance(archivo_csv, ArchivoCSV):
            self.archivos_csv.append(archivo_csv)
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

        