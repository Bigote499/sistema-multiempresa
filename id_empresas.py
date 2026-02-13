import pandas as pd
import re

def validar_email(email):
    patron = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return bool(re.match(patron, str(email)))


# Leer el CSV sin ID
df = pd.read_csv(r"C:\Plantilla csv\empresas.csv")

# Generar columna ID automáticamente (empezando en 1)
df.insert(0, "ID", range(1, len(df) + 1))

# Validar correos electrónicos y marcar inválidos
df['Email_Valido'] = df['Email'].apply(validar_email)

# Exportar a Excel
df.to_excel(r"C:\Plantilla csv\empresas.xlsx", index=False)

print("Archivo Excel generado con ID automático.")