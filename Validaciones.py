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
            print(f"✓ Archivo CSV '{archivo_csv.nombre}' agregado al sistema")
        else:
            print("✗ Error: El objeto no es de tipo ArchivoCSV")
    
    def agregar_eeg(self, archivo_eeg):
        """
        Agrega un objeto ArchivoEEG al sistema.
        
        Parámetros:
        archivo_eeg : ArchivoEEG
        Objeto de tipo ArchivoEEG a agregar
        """
        if isinstance(archivo_eeg, ArchivoEEG):
            self.archivos_eeg.append(archivo_eeg)
            print(f"✓ Archivo EEG '{archivo_eeg.nombre}' agregado al sistema")
        else:
            print("✗ Error: El objeto no es de tipo ArchivoEEG")
    
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


