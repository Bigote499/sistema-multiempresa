import sys
from PyQt5.QtWidgets import QApplication
from interfaz_empresas import EmpresaApp

def main():
    app = QApplication(sys.argv)
    ventana = EmpresaApp()
    ventana.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()