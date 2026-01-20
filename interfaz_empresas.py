import os
import sys
import pandas as pd
import re
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLineEdit, QLabel, QFileDialog, QDialog, QFormLayout,
    QDialogButtonBox, QMessageBox
)
from extraer_web import extraer_empresas_desde_web
from utilidades import obtener_proximo_id
from PyQt5.QtWidgets import QInputDialog
from openpyxl import load_workbook
from format_excel import formatear_excel
from db_manager import get_session, Empresa

class EmpresaApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestión de Empresas")
        self.resize(900, 600)
        self.df = pd.DataFrame()

        layout = QVBoxLayout()

        # Filtro
        self.filtro = QLineEdit()
        self.filtro.setPlaceholderText("Filtrar por nombre...")
        self.filtro.textChanged.connect(self.filtrar)
        layout.addWidget(QLabel("Buscar empresa:"))
        layout.addWidget(self.filtro)

        # Tabla
        self.tabla = QTableWidget()
        layout.addWidget(self.tabla)

        self.input_cliente = QLineEdit()
        self.input_cliente.setPlaceholderText("Nombre del cliente (ej. cliente_a)")
        layout.addWidget(QLabel("Cliente:"))
        layout.addWidget(self.input_cliente)

        # Botones
        btn_manual = QPushButton("Ingresar empresa manualmente")
        btn_manual.clicked.connect(self.ingresar_empresa_manual)
        layout.addWidget(btn_manual)

        btn_elegir_db = QPushButton("Elegir DB a actualizar")
        btn_elegir_db.clicked.connect(self.cargar_db_cliente)
        layout.addWidget(btn_elegir_db)

        btn_cargar = QPushButton("Reordenar Excel externo")
        btn_cargar.clicked.connect(self.reordenar_excel)
        layout.addWidget(btn_cargar)

        btn_editar = QPushButton("Editar selección")
        btn_editar.clicked.connect(self.editar_seleccion)
        layout.addWidget(btn_editar)

        btn_scrap = QPushButton("Extraer desde Web")
        btn_scrap.clicked.connect(self.extraer_desde_web)
        layout.addWidget(btn_scrap)

        btn_limpiar = QPushButton("Limpiar y validar")
        btn_limpiar.clicked.connect(self.limpiar_y_validar)
        layout.addWidget(btn_limpiar)

        btn_guardar_db = QPushButton("Guardar en base del cliente")
        btn_guardar_db.clicked.connect(self.guardar_en_db_cliente)
        layout.addWidget(btn_guardar_db)

        btn_guardar_excel = QPushButton("Convertir DB a Excel")
        btn_guardar_excel.clicked.connect(self.convertir_db_a_excel)
        layout.addWidget(btn_guardar_excel)

        self.setLayout(layout)

    def ingresar_empresa_manual(self):
        cliente = self.input_cliente.text().strip()
        if not cliente:
            QMessageBox.warning(self, "Cliente requerido", "Ingresá el nombre del cliente.")
            return

        dialogo = QDialog(self)
        dialogo.setWindowTitle("Agregar empresa")
        form = QFormLayout(dialogo)

        entradas = {}
        for campo in ["nombre", "cuit", "email", "web", "domicilio", "contacto"]:
            entrada = QLineEdit()
            if campo == "cuit":
                # Máscara para guiar al usuario en el formato del CUIT
                entrada.setInputMask("00-00000000-0;_")
            form.addRow(campo.capitalize() + ":", entrada)
            entradas[campo] = entrada

        botones = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        form.addWidget(botones)

        def aceptar():
            try:
                nombre = entradas["nombre"].text().strip()
                cuit = entradas["cuit"].text().strip()
                email = entradas["email"].text().strip()
                web = entradas["web"].text().strip()
                domicilio = entradas["domicilio"].text().strip()
                contacto = entradas["contacto"].text().strip()

                # Validación y formateo del CUIT
                from guardar_datos import validar_cuit
                cuit_formateado = validar_cuit(cuit)

                if not nombre or cuit_formateado is None:
                    QMessageBox.warning(dialogo, "Validación", "CUIT inválido o nombre vacío.")
                    return

                from db_manager import insertar_empresa, listar_empresas
                resultado = insertar_empresa(cliente, nombre, cuit_formateado, email, web, domicilio, contacto)

                if resultado.get("ok"):
                    QMessageBox.information(dialogo, "Éxito", f"Empresa '{nombre}' agregada a {cliente}.db")
                    # refrescar tabla desde DB
                    empresas = listar_empresas(cliente)
                    df = pd.DataFrame([{
                        "id": e.id,
                        "nombre": e.nombre,
                        "cuit": e.cuit,
                        "email": e.email,
                        "web": e.web,
                        "domicilio": e.domicilio,
                        "contacto": e.contacto
                    } for e in empresas])
                    self.df = df
                    self.mostrar_datos(self.df)
                    dialogo.accept()
                else:
                    QMessageBox.warning(dialogo, "Error", f"No se pudo guardar: {resultado.get('motivo')}")
            except Exception as e:
                QMessageBox.critical(dialogo, "Error", f"Ocurrió un error:\n{str(e)}")

        botones.accepted.connect(aceptar)
        botones.rejected.connect(dialogo.reject)
        dialogo.exec_()

    def mostrar_datos(self, df):
        df = df.astype(str).fillna("")
        df = df.copy()
        if "id" not in df.columns:
            df.insert(0, "id", range(1, len(df) + 1))
        self.df = df
        self.tabla.setRowCount(len(df))
        self.tabla.setColumnCount(len(df.columns))
        self.tabla.setHorizontalHeaderLabels(df.columns)
        for i, fila in df.iterrows():
            for j, valor in enumerate(fila):
                self.tabla.setItem(i, j, QTableWidgetItem(str(valor)))

    def filtrar(self):
        if "nombre" not in self.df.columns:
            return
        texto = self.filtro.text().lower()
        filtrado = self.df[self.df["nombre"].str.lower().str.contains(texto)]
        self.mostrar_datos(filtrado)

    def cargar_db_cliente(self):
        try:
            archivo, _ = QFileDialog.getOpenFileName(
                self,
                "Seleccionar base de datos",
                "c:/Plantilla csv",  # Ruta inicial
                "Bases de datos (*.db)"
            )
            if not archivo:
                return

            import os
            cliente = os.path.splitext(os.path.basename(archivo))[0]
            self.input_cliente.setText(cliente)

            from db_manager import listar_empresas
            empresas = listar_empresas(cliente)

            if not empresas:
                QMessageBox.information(self, "Base vacía", f"{cliente}.db no tiene empresas registradas.")
                self.df = pd.DataFrame()
                self.mostrar_datos(self.df)
                return

            df = pd.DataFrame(empresas)

            self.df = df
            self.mostrar_datos(self.df)
            QMessageBox.information(self, "DB cargada", f"Datos de {cliente}.db cargados para edición.")

        except Exception as e:
            QMessageBox.critical(self, "Error al cargar DB", f"Ocurrió un error:\n{str(e)}")
    
    def editar_seleccion(self):
        fila = self.tabla.currentRow()
        if fila < 0:
            QMessageBox.warning(self, "Sin selección", "Seleccioná una fila para editar.")
            return

        valores = {col: self.tabla.item(fila, j).text() if self.tabla.item(fila, j) else ""
                   for j, col in enumerate(self.df.columns)}

        dialogo = QDialog(self)
        dialogo.setWindowTitle("Editar empresa")
        form = QFormLayout(dialogo)
        entradas = {}
        for campo in ["nombre", "cuit", "email", "web", "domicilio", "contacto"]:
            entrada = QLineEdit(valores.get(campo, ""))
            if campo == "cuit":
                # Máscara para guiar al usuario en el formato del CUIT
                entrada.setInputMask("00-00000000-0;_")
            form.addRow(campo.capitalize() + ":", entrada)
            entradas[campo] = entrada

            

        botones = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        form.addWidget(botones)

        def aceptar():
            try:
                editados = {c: e.text().strip() for c, e in entradas.items()}
                from guardar_datos import validar_cuit

                # Validar y formatear CUIT antes de actualizar
                cuit_formateado = validar_cuit(editados["cuit"])
                if not editados["nombre"] or cuit_formateado is None:
                    QMessageBox.warning(dialogo, "Validación", "CUIT inválido o nombre vacío.")
                    return

                # Reemplazar el CUIT en el diccionario por el formateado
                editados["cuit"] = cuit_formateado

                if "id" in self.df.columns:  # edición en DB
                    cliente = self.input_cliente.text().strip()
                    if not cliente:
                        QMessageBox.warning(self, "Cliente requerido", "Ingresá el nombre del cliente.")
                        return
                    id_empresa = int(self.tabla.item(fila, 0).text())
                    from db_manager import actualizar_empresa, listar_empresas
                    resultado = actualizar_empresa(cliente, id_empresa, **editados)
                    if resultado.get("ok"):
                        QMessageBox.information(dialogo, "Éxito", f"Empresa {id_empresa} actualizada en {cliente}.db")
                        empresas = listar_empresas(cliente)
                        df = pd.DataFrame(empresas)
                        self.df = df
                        self.mostrar_datos(self.df)
                        dialogo.accept()
                    else:
                        QMessageBox.warning(dialogo, "Error", f"No se pudo actualizar: {resultado.get('motivo')}")
                else:  # edición en Excel
                    for c, v in editados.items():
                        if c in self.df.columns:
                            self.df.at[fila, c] = str(v)
                    self.mostrar_datos(self.df)
                    dialogo.accept()
            except Exception as e:
                QMessageBox.critical(dialogo, "Error", f"Ocurrió un error:\n{str(e)}")

        botones.accepted.connect(aceptar)
        botones.rejected.connect(dialogo.reject)
        dialogo.exec_()

    def reordenar_excel(self):
        archivo, _ = QFileDialog.getOpenFileName(self, "Seleccionar Excel", "", "Excel (*.xlsx)")
        if archivo:
            df = pd.read_excel(archivo)
            columnas_objetivo = ["Nombre", "Email", "web", "Domicilio", "Contacto"]
            mapa = {c.strip().lower(): c for c in df.columns}
            seleccionadas = [mapa.get(c.lower()) for c in columnas_objetivo if c.lower() in mapa]
            df_filtrado = df[seleccionadas]
            df_filtrado = df_filtrado.astype(str).fillna("")
            if "CUIT" not in df_filtrado.columns:
                df_filtrado["CUIT"] = ""
            self.df = df_filtrado
            self.mostrar_datos(self.df)

    

    def extraer_desde_web(self):
        url, ok = QInputDialog.getText(self, "Ingresar URL", "Pegá la URL de la web:")
        if ok and url:
            empresas = extraer_empresas_desde_web(url)
            if empresas is not None:
                empresas = empresas.astype(str).fillna("")
                self.df = pd.concat([self.df, empresas], ignore_index=True)
                self.mostrar_datos(self.df)
                QMessageBox.information(self, "Extracción completa", "Los datos se extrajeron correctamente desde la web.")
            else:
                QMessageBox.warning(self, "Error", "No se pudo extraer datos desde la URL.")
        

    def limpiar_y_validar(self):
        if self.df.empty:
            QMessageBox.warning(self, "Sin datos", "No hay datos para limpiar.")
            return

        df = self.df.copy()

        # Normalizar nombres de columnas esperadas
        mapa_cols = {
            "Nombre": "nombre",
            "CUIT": "cuit",
            "cuit": "cuit",
            "Email": "email", 
            "web": "web",
            "Domicilio": "domicilio",  
            "Contacto": "contacto"
        }
        df = df.rename(columns={k: v for k, v in mapa_cols.items() if k in df.columns})

        # Reemplazar NaN por vacío
        df = df.fillna("")

        # Trims y lower donde corresponde
        for c in ["nombre", "cuit", "email", "web", "domicilio", "contacto"]:
            if c in df.columns:
                df[c] = df[c].astype(str).str.strip()

        # Normalizar web (agregar https:// si falta)
        if "web" in df.columns:
            def norm_web(u):
                if not u: return ""
                u = u.strip()
                if not re.match(r"^https?://", u):
                    return "https://" + u
                return u
            df["web"] = df["web"].apply(norm_web)

        # Normalizar email (minúsculas y quitar espacios)
        if "Email" in df.columns:
            df["Email"] = df["Email"].str.lower().str.replace(" ", "", regex=False)

        # Completar email desde dominio web si falta (heurística simple)
        if "Email" in df.columns and "Nombre" in df.columns and "web" in df.columns:
            def completar_email(row):
                if row["Email"]: return row["Email"]
                if row["web"]:
                    dominio = re.sub(r"^https?://", "", row["web"]).split("/")[0]
                    dominio = dominio.replace("www.", "")
                    base = re.sub(r"\s+", "", row["Nombre"]).lower()
                    return f"contacto@{dominio}" if dominio else ""
                return ""
            df["Email"] = df.apply(completar_email, axis=1)

        # Validaciones mínimas
        errores = []
        for i, r in df.iterrows():
            if not r.get("nombre"):
                errores.append(f"Fila {i+1}: falta Nombre")
            if not r.get("web"):
                errores.append(f"Fila {i+1}: falta Web")
            if not r.get("cuit"):
                errores.append(f"Fila {i+1}: falta CUIT")
            else:
                from guardar_datos import validar_cuit

                # Dentro del bucle de validación
                cuit = str(r.get("cuit")).strip()
                if validar_cuit(cuit) is None:
                    errores.append(f"Fila {i+1}: CUIT inválido ({cuit})")
            # Email formato básico
            em = r.get("email", "")
            if em and not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", em):
                errores.append(f"Fila {i+1}: Email inválido ({em})")

        if errores:
            QMessageBox.warning(self, "Validación", "Revisá:\n" + "\n".join(errores))
            # No actualizamos self.df si hay errores—que el usuario corrija
            return

        # Deduplicar por Nombre+Web (ajustable)
        if {"Nombre", "web", "CUIT"}.issubset(df.columns):
            df = df.drop_duplicates(subset=["Nombre", "CUIT", "web"])

        # Actualizar y mostrar
        self.df = df
        self.mostrar_datos(self.df)
        QMessageBox.information(self, "Limpieza completa", "Datos normalizados y validados.")

    def guardar_en_db_cliente(self):
        from guardar_datos import guardar_en_db

        cliente = self.input_cliente.text().strip()
        if not cliente:
            QMessageBox.warning(self, "Cliente requerido", "Ingresá el nombre del cliente.")
            return

        if self.df.empty:
            QMessageBox.warning(self, "Sin datos", "No hay datos para guardar.")
            return

        # Normalizar nombres de columnas ANTES de guardar
        self.df = self.df.rename(columns={
            "Nombre": "nombre",
            "CUIT": "cuit",
            "Email": "email",
            "web": "web",
            "Domicilio": "domicilio",
            "Contacto": "contacto"
        })

        try:
            resumen = guardar_en_db(cliente, self.df)

            # Mostrar resumen en la interfaz
            mensaje = (
                f"Guardadas: {resumen['guardadas']}\n"
                f"Omitidas: {resumen['omitidas']}\n"
                f"Errores: {resumen['errores']}"
            )
            QMessageBox.information(self, "Resultado del guardado", mensaje)

            print(f"[OK] Guardadas: {resumen['guardadas']} | [ADVERTENCIA] Omitidas: {resumen['omitidas']} | [ERROR] {resumen['errores']}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Ocurrió un error al guardar en {cliente}.db:\n{str(e)}")
            print(f"[ERROR] No se pudo guardar en {cliente}.db: {e}")
    
    def convertir_db_a_excel(self):
    
        # Seleccionar base de datos
        ruta_db, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar base de datos", "", "Bases de datos (*.db)"
        )
        if not ruta_db:
            return

        cliente = os.path.splitext(os.path.basename(ruta_db))[0]
        self.input_cliente.setText(cliente)  # opcional: actualizar campo cliente

        # Seleccionar archivo de salida Excel
        nombre_archivo = QFileDialog.getSaveFileName(
            self, "Convertir DB a Excel", "", "Archivos Excel (*.xlsx)"
        )[0]
        if not nombre_archivo:
            return
        if not nombre_archivo.endswith(".xlsx"):
            nombre_archivo += ".xlsx"

        try:
            # Obtener datos dentro de la sesión
            with get_session(cliente) as (session, _):
                empresas = session.query(Empresa).all()
                data = [{
                    "id": e.id,
                    "nombre": e.nombre,
                    "cuit": e.cuit,
                    "email": e.email,
                    "web": e.web,
                    "domicilio": e.domicilio,
                    "contacto": e.contacto
                } for e in empresas]

            # Convertir a DataFrame y exportar
            df = pd.DataFrame(
                data,
                columns=["id", "nombre", "cuit", "email", "web", "domicilio", "contacto"]
            )
            df.to_excel(nombre_archivo, index=False)

            # Mejorar formato con openpyxl
            wb = load_workbook(nombre_archivo)
            ws = wb.active

            formatear_excel(ws)
            wb.save(nombre_archivo)

            QMessageBox.information(
                self,
                "Conversión completa",
                f"Datos exportados desde {cliente}.db a {nombre_archivo}"
            )
            print(f"[OK] Exportado {cliente}.db a {nombre_archivo}")

        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"No se pudo exportar datos desde {cliente}.db\n{e}"
            )
            print(f"[ERROR] Falló la exportación de {cliente}.db: {e}")

   
if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = EmpresaApp()
    ventana.show()
    sys.exit(app.exec_())