import csv

ruta = r"C:\Plantilla csv\empresas.csv"

with open(ruta, newline='', encoding='utf-8') as archivo:
    lector = csv.reader(archivo)
    for i, fila in enumerate(lector, start=1):
        print(f"Fila {i}: {len(fila)} columnas → {fila}")