from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
import pandas as pd

# Cargar datos
df = pd.read_excel("empresas.xlsx")  # O directamente desde CSV si preferís

# Convertir a lista de listas
datos = [df.columns.tolist()] + df.values.tolist()

# Crear documento PDF
doc = SimpleDocTemplate("reporte_empresas.pdf", pagesize=A4)
elementos = []

# Estilos
estilos = getSampleStyleSheet()
titulo = Paragraph("Reporte de Empresas", estilos["Title"])
elementos.append(titulo)
elementos.append(Spacer(1, 12))

# Tabla
tabla = Table(datos)
tabla.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), colors.lightblue),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
    ("FONTSIZE", (0, 0), (-1, -1), 8),
]))

elementos.append(tabla)

# Pie de página
elementos.append(Spacer(1, 24))
pie = Paragraph("Generado automáticamente con Python y ReportLab", estilos["Normal"])
elementos.append(pie)

# Exportar
doc.build(elementos)
print("PDF generado correctamente.")