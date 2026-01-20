import sys
import pandas as pd
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLineEdit, QLabel, QMessageBox, QFileDialog
)
from guardar_datos import guardar_en_db, db_a_excel


class EmpresaApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestión de Empresas")
        self.resize(800, 600)

        # Intentar cargar datos desde CSV inicial (solo demo)
        try:
            self.df = pd.read_csv("empresas.csv")
        except Exception:
            self.df = pd.DataFrame(columns=["Nombre", "CUIT", "Email", "web", "Domicilio", "Contacto"])

        # Layout principal
        layout = QVBoxLayout()

        # Campo cliente
        self.input_cliente = QLineEdit()
        self.input_cliente.setPlaceholderText("Nombre del cliente...")
        layout.addWidget(QLabel("Cliente:"))
        layout.addWidget(self.input_cliente)

        # Filtro por nombre
        self.filtro = QLineEdit()
        self.filtro.setPlaceholderText("Filtrar por nombre...")
        self.filtro.textChanged.connect(self.filtrar)
        layout.addWidget(QLabel("Buscar empresa:"))
        layout.addWidget(self.filtro)

        # Tabla
        self.tabla = QTableWidget()
        layout.addWidget(self.tabla)
        self.mostrar_datos(self.df)

        # Botón guardar en DB
        btn_db = QPushButton("Guardar en base del cliente")
        btn_db.clicked.connect(self.guardar_en_db_cliente)
        layout.addWidget(btn_db)

        # Botón exportar DB a Excel
        btn_excel = QPushButton("Exportar DB a Excel")
        btn_excel.clicked.connect(self.exportar_db_excel)
        layout.addWidget(btn_excel)

        self.setLayout(layout)

    def mostrar_datos(self, df):
        self.tabla.setRowCount(len(df))
        self.tabla.setColumnCount(len(df.columns))
        self.tabla.setHorizontalHeaderLabels(df.columns)

        for i, fila in df.iterrows():
            for j, valor in enumerate(fila):
                self.tabla.setItem(i, j, QTableWidgetItem(str(valor)))

        self.tabla.resizeColumnsToContents()

    def filtrar(self):
        if "Nombre" not in self.df.columns:
            return
        texto = self.filtro.text().lower()
        filtrado = self.df[self.df["Nombre"].str.lower().str.contains(texto, na=False)]
        self.mostrar_datos(filtrado)

    def guardar_en_db_cliente(self):
        cliente = self.input_cliente.text().strip()
        if not cliente:
            QMessageBox.warning(self, "Cliente requerido", "Ingresá el nombre del cliente.")
            return
        if self.df.empty:
            QMessageBox.warning(self, "Sin datos", "No hay datos para guardar.")
            return

        resumen = guardar_en_db(cliente, self.df)
        mensaje = (
            f"Guardadas: {resumen['guardadas']}\n"
            f"Omitidas: {resumen['omitidas']}\n"
            f"Errores: {resumen['errores']}"
        )
        QMessageBox.information(self, "Resultado del guardado", mensaje)
        if resumen.get("cuit_invalidos", 0) > 0:
            QMessageBox.warning(
                self,
                "CUIT inválido",
                f"{resumen['cuit_invalidos']} fila(s) fueron omitidas por tener CUIT inválido.\n"
                "Recordá que el CUIT debe tener 11 dígitos numéricos."
            )

    def exportar_db_excel(self):
        cliente = self.input_cliente.text().strip()
        if not cliente:
            QMessageBox.warning(self, "Cliente requerido", "Ingresá el nombre del cliente.")
            return

        nombre_archivo, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar Excel desde DB",
            f"{cliente}_exportado.xlsx",
            "Archivos Excel (*.xlsx)"
        )
        if not nombre_archivo:
            return

        ok = db_a_excel(cliente, nombre_archivo)
        if ok:
            QMessageBox.information(self, "Exportación", f"Archivo Excel guardado en:\n{nombre_archivo}")
        else:
            QMessageBox.critical(self, "Error", "No se pudo exportar la DB a Excel.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = EmpresaApp()
    ventana.show()
    sys.exit(app.exec_())