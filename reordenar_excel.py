import pandas as pd

# Ruta del archivo externo
archivo_entrada = "archivo_externo.xlsx"
archivo_salida = "empresas_reordenado.xlsx"

# Columnas que queremos extraer (pueden tener nombres similares)
columnas_objetivo = ["Nombre", "CUIT", "Email", "web", "Domicilio", "Contacto"]

# Leer el archivo original
df = pd.read_excel(archivo_entrada)

# Buscar columnas similares (ignorando mayúsculas y espacios)
def normalizar(col):
    return col.strip().lower()

mapa = {normalizar(c): c for c in df.columns}
seleccionadas = [mapa.get(normalizar(c)) for c in columnas_objetivo if normalizar(c) in mapa]

# Extraer y guardar
df_filtrado = df[seleccionadas]
df_filtrado.to_excel(archivo_salida, index=False)
print("Archivo reordenado generado.")