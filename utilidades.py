import os
import pandas as pd

def obtener_proximo_id(nombre_archivo):
    if not os.path.exists(nombre_archivo):
        return 1

    try:
        df = pd.read_csv(nombre_archivo)
        if "ID" in df.columns and not df.empty:
            return int(df["ID"].max()) + 1
        else:
            return 1
    except Exception as e:
        print(f"Error al leer {nombre_archivo}: {e}")
        return 1
    
def verificar_existencia(nombre_archivo, nuevo_dato):
    """
    Verifica si ya existe un registro con el mismo CUIT, Nombre, Email o Web.
    - nombre_archivo: archivo CSV donde se guardan los datos
    - nuevo_dato: diccionario con los campos de la nueva empresa
    """
    import pandas as pd
    import os

    if not os.path.exists(nombre_archivo):
        return False, None  # si no existe el archivo, no hay duplicados

    try:
        df = pd.read_csv(nombre_archivo)

        # Normalizamos a minúsculas para evitar problemas de mayúsculas/minúsculas
        for campo in ["Nombre", "CUIT", "Email", "Web", "Domicilio", "Contacto"]:
            if campo in df.columns and campo in nuevo_dato:
                coincidencias = df[df[campo].str.lower() == str(nuevo_dato[campo]).lower()]
                if not coincidencias.empty:
                    return True, campo  # duplicado encontrado
        return False, None
    except Exception as e:
        print(f"Error al verificar duplicados: {e}")
        return False, None