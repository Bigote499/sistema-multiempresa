# Sistema Multiempresa

Este proyecto permite gestionar datos de múltiples empresas, almacenarlos en bases SQLAlchemy y exportarlos a Excel con formato profesional. Ideal para negocios, desarrolladores freelance o entornos administrativos.

## 🚀 Funcionalidades principales

- Alta, edición y eliminación de empresas desde interfaz gráfica (PyQt5).
- Exportación a Excel con:
  - Encabezados en negrita y mayúsculas
  - Filtros automáticos
  - Congelado de fila y columnas (ID y NOMBRE)
  - Ajuste automático de ancho de columnas
  - Alineación y ajuste de texto
- Validación de CUIT y campos de entrada.
- Separación modular del código (interfaz, lógica, utilidades, formato).
- Compatible con múltiples bases de datos `.db`.

## 🧱 Estructura del proyecto


sistema-multiempresa/
├── main.py                  # Punto de entrada de la aplicación
├── interfaz_empresas.py     # Ventana principal (PyQt5)
├── ventana_carga_empresas.py # Formulario de carga de datos
├── db_manager.py            # Conexión y operaciones con SQLAlchemy
├── guardar_datos.py         # Lógica para persistencia de datos
├── format_excel.py          # Formato profesional para exportación a Excel
├── excel_empresas.py        # Generación de archivos Excel
├── reporte_empresas.py      # Reportes y resúmenes
├── extraer_web.py           # Extracción de datos desde la web
├── utilidades.py            # Validaciones y funciones auxiliares
├── id_empresas.py           # Generación de IDs únicos
├── reordenar_excel.py       # Reorganización de columnas en Excel
├── requirements.txt         # Dependencias del proyecto
├── README.md                # Documentación del sistema
├── .gitignore               # Exclusión de archivos innecesarios

## ⚙️ Instalación

1. Clonar el repositorio:
   ```bash
   git clone https://github.com/tu_usuario/sistema-multiempresa.git
   cd sistema-multiempresa


2. Crear entorno virtual e instalar dependencias:
python -m venv venv
venv\Scripts\activate      # Windows
pip install -r requirements.txt

3. (Opcional) Instalar herramientas de desarrollo:
pip install -r dev-requirements.txt


🖥️ Compatibilidad
Este sistema fue desarrollado y probado en Windows 10/11 con Python 3.10+.
La arquitectura modular permite adaptarlo fácilmente a otros entornos como Linux o macOS, ajustando rutas y activación de entorno virtual según el sistema operativo.

▶️ Uso
Ejecutar la aplicación:
python main.py


📌 Próximos pasos
- Exportar múltiples tablas en hojas separadas.
- Agregar reportes PDF con ReportLab.
- Mejorar validaciones y mensajes de error.
- Documentación para despliegue en plataformas freelance.
🧠 Autor
Desarrollado por Sergio Sosa — apasionado por herramientas prácticas, modulares y profesionales para negocios reales.

📊 Ejemplo de salida (Excel exportado)
Al exportar los datos de empresas, el sistema genera un archivo .xlsx con formato profesional, listo para informes o auditorías. Las principales características del archivo son:
- Encabezados en negrita y mayúsculas
- Filtros automáticos activados
- Fila de encabezado y columnas clave congeladas
- Columnas con ancho ajustado automáticamente
- Texto alineado y ajustado para mejor lectura
Ejemplo de tabla exportada:
image/Excel_demo.png


## 📄 Licencia
Este proyecto se distribuye bajo la Licencia MIT.  
Consulta el archivo [LICENSE](LICENSE) para más detalles.

👉 ¿Querés ver una presentación visual orientada a clientes?  
Consultá el archivo [README_comercial.md](README_comercial.md)


