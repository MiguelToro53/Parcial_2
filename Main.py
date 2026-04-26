"""
main.py

Script principal del sistema explorador de archivos EEG (.MAT) y SIATA (.CSV).
 
El programa inicia un menú interactivo que permite:
  - Cargar archivos CSV y EEG las veces que se desee.
  - Aplicar todas las funcionalidades de cada clase.
  - Guardar gráficos automáticamente en carpetas organizadas.
 
Bibliotecas utilizadas:
    numpy, pandas, matplotlib, scipy
 
Estructura del proyecto:
    Validaciones.py  ← clases Sistema, ArchivoCSV, ArchivoEEG
    main.py          ← este archivo (menú e implementación)
    graficos_csv/    ← gráficos generados de archivos CSV
    graficos_eeg/    ← gráficos generados de archivos EEG
"""
 
from Validaciones import Sistema, ArchivoCSV, ArchivoEEG

# Utilidades de menú

def linea(caracter='=', largo=60):
    """Imprime una línea decorativa."""
    print(caracter * largo)
 
 
def titulo(texto):
    """Imprime un bloque de título."""
    linea()
    print(f"   {texto}")
    linea()
 
 
def pedir_entero(mensaje, minimo=None, maximo=None):
    """
    Solicita un número entero al usuario con validación de rango.
 
    Parámetros:
    
    mensaje : str
        Texto que se muestra al usuario.
    minimo : int, opcional
        Valor mínimo permitido.
    maximo : int, opcional
        Valor máximo permitido.
 
    Retorna:
    
    int : el valor ingresado y validado.
    """
    while True:
        try:
            valor = int(input(mensaje))
            if minimo is not None and valor < minimo:
                print(f"     Ingrese un valor ≥ {minimo}.")
                continue
            if maximo is not None and valor > maximo:
                print(f"     Ingrese un valor ≤ {maximo}.")
                continue
            return valor
        except ValueError:
            print("     Ingrese un número entero válido.")
 
 
def pedir_opcion(opciones_validas, mensaje="   Opción: "):
    """
    Solicita una opción de un conjunto válido.
 
    Parámetros:
    
    opciones_validas : list[str]
        Conjunto de opciones aceptadas.
    mensaje : str
        Texto de prompt.
 
    Retorna:
    
    str : la opción elegida (en minúsculas).
    """
    while True:
        opcion = input(mensaje).strip().lower()
        if opcion in opciones_validas:
            return opcion
        print(f"     Opción no válida. Elija entre: {opciones_validas}")
 
 
def seleccionar_objeto(lista, tipo_nombre):
    """
    Permite al usuario seleccionar un objeto de una lista numerada.
 
    Parámetros:
    
    lista : list
        Lista de objetos con atributo 'nombre'.
    tipo_nombre : str
        Nombre del tipo para los mensajes (ej. 'CSV', 'EEG').
 
    Retorna:
    
    objeto seleccionado o None si la lista está vacía.
    """
    if not lista:
        print(f"\n   No hay archivos {tipo_nombre} cargados todavía.")
        return None
 
    print(f"\n   Archivos {tipo_nombre} disponibles:")
    for i, obj in enumerate(lista, 1):
        print(f"   {i}. {obj.nombre}")
 
    idx = pedir_entero("   Seleccione número: ", minimo=1, maximo=len(lista))
    return lista[idx - 1]
