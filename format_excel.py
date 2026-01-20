from openpyxl.styles import Font, Alignment

def formatear_excel(ws):
    # Negrita y mayúsculas en encabezados
    for cell in ws[1]:
        if cell.value:
            cell.value = str(cell.value).upper()
        cell.font = Font(bold=True)

    # Filtros automáticos
    ws.auto_filter.ref = ws.dimensions

    # Congelar primera fila + columnas ID y NOMBRE
    ws.freeze_panes = "C2"

    # Ajuste de texto en todas las celdas
    for row in ws.iter_rows():
        for cell in row:
            cell.alignment = Alignment(wrap_text=True)

    # Ajuste automático de ancho de columnas
    for col in ws.columns:
        col_letter = col[0].column_letter
        max_length = max(len(str(cell.value)) if cell.value else 0 for cell in col)
        extra = 4 if col_letter in ["F", "G"] else 2  # más espacio para DOMICILIO y CONTACTO
        ws.column_dimensions[col_letter].width = max_length + extra