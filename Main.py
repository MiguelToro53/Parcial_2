"""
main.py

Script principal del sistema explorador de archivos EEG (.MAT) y SIATA (.CSV).
 
El programa inicia un menú interactivo que permite:
  - Cargar archivos CSV y EEG las veces que se desee.
  - Aplicar todas las funcionalidades de cada clase.
  - Guardar gráficos automáticamente en carpetas organizadas.
 
Bibliotecas utilizadas:
    numpy, pandas, matplotlib, scipy, json
 
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

# Sub-menús

def submenu_csv(sistema):
    """
    Sub-menú completo para la gestión y procesamiento de archivos CSV.
 
    Parámetros:

    sistema : Sistema
        Instancia del gestor central.
    """
    while True:
        titulo("MENÚ CSV – SIATA (Calidad del Aire)")
        print("   1. Cargar nuevo archivo CSV")
        print("   2. Mostrar info() del archivo")
        print("   3. Mostrar describe() del archivo")
        print("   4. Gráficos (plot / boxplot / histograma) de una columna")
        print("   5. Operación apply()  – raíz cuadrada de una columna")
        print("   6. Operación map()    – categorizar columna (Bajo/Medio/Alto)")
        print("   7. Operación suma / resta de dos columnas")
        print("   8. Convertir columna de fechas a índice (set_index)")
        print("   9. Resample y gráficos temporales (diario/mensual/trimestral)")
        print("   10. Resetear datos al estado original")
        print("   0. Volver al menú principal")
        linea('-')
 
        opcion = pedir_opcion(
            ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10']
        )
 
        # Cargar nuevo CSV 
        if opcion == '1':
            ruta = input("\n   Ruta del archivo CSV: ").strip()
            nombre = input("   Nombre descriptivo (Enter para usar nombre del archivo): ").strip()
            nombre = nombre if nombre else None
            try:
                nuevo = ArchivoCSV(ruta, nombre)
                sistema.agregar_csv(nuevo)
            except Exception as e:
                print(f"   Error al cargar: {e}")
 
        #  Seleccionar CSV para las demás opciones 
        elif opcion in ['2', '3', '4', '5', '6', '7', '8', '9', '10']:
            archivo = seleccionar_objeto(sistema.archivos_csv, "CSV")
            if archivo is None:
                continue
 
            if opcion == '2':
                archivo.mostrar_info()
 
            elif opcion == '3':
                archivo.mostrar_describe()
 
            elif opcion == '4':
                print(f"\n   Columnas disponibles: {list(archivo.df.columns)}")
                col = input("   Nombre de la columna a graficar: ").strip()
                archivo.graficar_columna(col)
 
            elif opcion == '5':
                print(f"\n   Columnas disponibles: {list(archivo.df.columns)}")
                col = input("   Nombre de la columna: ").strip()
                archivo.aplicar_operacion_apply(col)
 
            elif opcion == '6':
                print(f"\n   Columnas disponibles: {list(archivo.df.columns)}")
                col = input("   Nombre de la columna: ").strip()
                archivo.aplicar_operacion_map(col)
 
            elif opcion == '7':
                print(f"\n   Columnas disponibles: {list(archivo.df.columns)}")
                col1 = input("   Primera columna: ").strip()
                col2 = input("   Segunda columna: ").strip()
                print("   Operación: (s)uma / (r)esta")
                op = pedir_opcion(['s', 'r'], "   Opción: ")
                operacion = 'suma' if op == 's' else 'resta'
                archivo.sumar_restar_columnas(col1, col2, operacion)
 
            elif opcion == '8':
                print(f"\n   Columnas disponibles: {list(archivo.df.columns)}")
                col_fecha = input(
                    "   Nombre de la columna de fechas [Enter = 'fecha_hora']: "
                ).strip()
                col_fecha = col_fecha if col_fecha else 'fecha_hora'
                archivo.convertir_fecha_indice(col_fecha)
 
            elif opcion == '9':
                # Verificar que el índice sea datetime antes de seguir
                import pandas as pd
                if not isinstance(archivo.df.index, pd.DatetimeIndex):
                    print("\n     El índice no es datetime.")
                    print("   Use primero la opción 8 (convertir_fecha_indice).")
                else:
                    print(f"\n   Columnas disponibles: {list(archivo.df.columns)}")
                    col = input("   Columna a graficar en el resample: ").strip()
                    archivo.graficar_resample(col)
 
            elif opcion == '10':
                archivo.resetear_datos()
 
        elif opcion == '0':
            break

def submenu_eeg(sistema):
    """
    Sub-menú completo para la gestión y procesamiento de archivos EEG (.MAT).
 
    Parámetros:
    
    sistema : Sistema
        Instancia del gestor central.
    """
    while True:
        titulo("MENÚ EEG – Electroencefalografías (.MAT)")
        print("   1. Cargar nuevo archivo EEG (.MAT)")
        print("   2. Mostrar estructura del archivo (whosmat)")
        print("   3. Proceso 1 – Seleccionar 3 canales, sumar y graficar (2D)")
        print("   4. Proceso 2 – Promedio y desviación estándar con stem plots (3D)")
        print("   5. Resetear datos al estado original")
        print("   0. Volver al menú principal")
        linea('-')
 
        opcion = pedir_opcion(['0', '1', '2', '3', '4', '5'])
 
        #  Cargar nuevo EEG 
        if opcion == '1':
            ruta = input("\n   Ruta del archivo .MAT: ").strip()
            nombre = input("   Nombre descriptivo (Enter para usar nombre del archivo): ").strip()
            nombre = nombre if nombre else None
            try:
                nuevo = ArchivoEEG(ruta, nombre)
                sistema.agregar_eeg(nuevo)
            except Exception as e:
                print(f"   Error al cargar: {e}")
 
        elif opcion in ['2', '3', '4', '5']:
            archivo = seleccionar_objeto(sistema.archivos_eeg, "EEG")
            if archivo is None:
                continue
 
            if opcion == '2':
                archivo.mostrar_whosmat()
 
            elif opcion == '3':
                # Proceso 1
                n_canales = archivo.data.shape[0]
                n_muestras = archivo.data.shape[1]
                n_epocas = archivo.data.shape[2]
 
                print(f"\n   Archivo: {archivo.nombre}")
                print(f"   Canales disponibles : 0 – {n_canales - 1}")
                print(f"   Rango de muestras   : 0 – {n_muestras - 1}")
                print(f"   Épocas disponibles  : 0 – {n_epocas - 1}")
 
                print("\n   Ingrese 3 canales:")
                c1 = pedir_entero(f"   Canal 1 (0–{n_canales-1}): ", 0, n_canales - 1)
                c2 = pedir_entero(f"   Canal 2 (0–{n_canales-1}): ", 0, n_canales - 1)
                c3 = pedir_entero(f"   Canal 3 (0–{n_canales-1}): ", 0, n_canales - 1)
 
                p_min = pedir_entero(f"   Punto mínimo (0–{n_muestras-2}): ", 0, n_muestras - 2)
                p_max = pedir_entero(f"   Punto máximo ({p_min+1}–{n_muestras-1}): ",
                                     p_min + 1, n_muestras - 1)
                epoca = pedir_entero(f"   Época (0–{n_epocas-1}): ", 0, n_epocas - 1)
 
                archivo.proceso1_sumar_canales([c1, c2, c3], p_min, p_max, epoca)
 
            elif opcion == '4':
                # Proceso 2
                print(f"\n   Archivo: {archivo.nombre}")
                print(f"   Shape: {archivo.data.shape} (canales, muestras, épocas)")
                print("\n   Eje de reducción:")
                print("     0 → reducir sobre canales   → resultado (muestras × épocas)")
                print("     1 → reducir sobre muestras  → resultado (canales × épocas)")
                print("     2 → reducir sobre épocas    → resultado (canales × muestras)  ← recomendado")
                eje = pedir_entero("   Eje (0, 1 o 2): ", 0, 2)
                archivo.proceso2_promedio_desviacion(eje)
 
            elif opcion == '5':
                archivo.resetear_datos()
 
        elif opcion == '0':
            break

# Menú principal

def menu_principal():
    """
    Función principal que inicializa el sistema y muestra el menú interactivo.
    Loop principal del programa; se ejecuta hasta que el usuario elija salir.
    """
    sistema = Sistema()
 
    print("\n" + "="*60)
    print("   SISTEMA EXPLORADOR DE ARCHIVOS EEG Y SIATA")
    print("   Proyecto de Procesamiento de Señales")
    print("="*60)
    print("   Bienvenido al sistema. Cargue archivos CSV o EEG")
    print("   y explore sus datos de forma interactiva.")

    # Al crear el Sistema, _cargar_estado() se ejecuta automáticamente
    # y recupera todos los archivos registrados en sesiones anteriores
    sistema = Sistema()
 
    total = len(sistema.archivos_csv) + len(sistema.archivos_eeg)
    if total == 0:
        print("   Bienvenido. No hay archivos de sesiones anteriores.")
        print("   Cargue archivos CSV o EEG desde el menú.")
    else:
        print("   Sesión restaurada. Use la opción 3 para ver los archivos cargados.")
 
    while True:
        titulo("MENÚ PRINCIPAL")
        print("   1. Gestión de archivos CSV (SIATA – Calidad del Aire)")
        print("   2. Gestión de archivos EEG (.MAT – Electroencefalografías)")
        print("   3. Listar todos los archivos cargados en el sistema")
        print("   0. Salir")
        linea('-')
 
        opcion = pedir_opcion(['0', '1', '2', '3'])
 
        if opcion == '1':
            submenu_csv(sistema)
 
        elif opcion == '2':
            submenu_eeg(sistema)
 
        elif opcion == '3':
            sistema.listar_archivos()
 
        elif opcion == '0':
            linea()
            print(" Esto me saco canas")
            linea()
            break

if __name__ == "__main__":
    menu_principal()
