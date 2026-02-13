from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker
from contextlib import contextmanager
import pandas as pd

# -------------------------------
# Base y modelo
# -------------------------------
Base = declarative_base()

class Empresa(Base):
    __tablename__ = "empresas"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String, unique=True, nullable=False, index=True)
    cuit = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, nullable=True)     # no unique
    web = Column(String, nullable=True)       # no unique
    domicilio = Column(String, nullable=True) # no unique
    contacto = Column(String, nullable=True)  # teléfono/celular, no unique

    def __repr__(self):
        return f"<Empresa(nombre={self.nombre}, cuit={self.cuit})>"

# -------------------------------
# Sesión por cliente
# -------------------------------
def crear_sesion(cliente):
    """Crea una sesión SQLAlchemy para un cliente específico."""
    engine = create_engine(f"sqlite:///{cliente}.db", echo=False)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session(), engine

@contextmanager
def get_session(cliente):
    """Context manager para manejar sesión con commit/rollback automático."""
    session, engine = crear_sesion(cliente)
    try:
        yield session, engine
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

# -------------------------------
# Utilidades
# -------------------------------
def limpiar_texto(s):
    return (str(s).strip() if s is not None else "").strip()

def validar_cuit(cuit):
    """Valida que el CUIT tenga 11 dígitos numéricos y lo formatea."""
    cuit = limpiar_texto(cuit)
    numeros = ''.join(filter(str.isdigit, cuit))
    if len(numeros) == 11:
        return f"{numeros[0:2]}-{numeros[2:10]}-{numeros[10]}"
    return None

# -------------------------------
# Funciones de gestión
# -------------------------------
def insertar_empresa(cliente, nombre, cuit, email=None, web=None, domicilio=None, contacto=None):
    """Inserta una nueva empresa en la base del cliente con validación."""
    nombre = limpiar_texto(nombre)
    cuit = limpiar_texto(cuit)
    email = limpiar_texto(email)
    web = limpiar_texto(web)
    domicilio = limpiar_texto(domicilio)
    contacto = limpiar_texto(contacto)

    cuit_validado = validar_cuit(cuit)
    if not nombre or cuit_validado is None:
        print(" Error: nombre vacío o CUIT inválido.")
        return {"ok": False, "motivo": "validacion"}

    try:
        with get_session(cliente) as (session, _):
            # Evitar duplicados manualmente para feedback claro
            existe = session.query(Empresa).filter(
                (Empresa.cuit == cuit_validado) | (Empresa.nombre == nombre)
            ).first()
            if existe:
                print(" Duplicado: ya existe empresa con ese nombre o CUIT.")
                return {"ok": False, "motivo": "duplicado"}

            nueva = Empresa(
                nombre=nombre,
                cuit=cuit_validado,
                email=email or None,
                web=web or None,
                domicilio=domicilio or None,
                contacto=contacto or None
            )
            session.add(nueva)
            print(f" Empresa guardada en {cliente}.db: {nombre}")
            return {"ok": True}
    except Exception as e:
        print(f" Error al guardar empresa en {cliente}.db: {e}")
        return {"ok": False, "motivo": "error"}

def actualizar_empresa(cliente, id_empresa, **campos):
    """Actualiza los datos de una empresa existente en la DB."""
    with get_session(cliente) as (session, _):
        empresa = session.query(Empresa).filter_by(id=id_empresa).first()
        if not empresa:
            return {"ok": False, "motivo": "no_encontrada"}
        if "cuit" in campos:
            cuit_validado = validar_cuit(campos["cuit"])
            if cuit_validado is None:
                return {"ok": False, "motivo": "cuit_invalido"}
            campos["cuit"] = cuit_validado
        if "nombre" in campos and not limpiar_texto(campos["nombre"]):
            return {"ok": False, "motivo": "nombre_vacio"}
        for campo, valor in campos.items():
            if hasattr(empresa, campo):
                setattr(empresa, campo, limpiar_texto(valor))
        return {"ok": True}

def listar_empresas(cliente):
    """Devuelve todas las empresas del cliente como diccionarios."""
    with get_session(cliente) as (session, _):
        empresas = session.query(Empresa).all()
        return [{
            "id": e.id,
            "nombre": e.nombre,
            "cuit": e.cuit,
            "email": e.email,
            "web": e.web,
            "domicilio": e.domicilio,
            "contacto": e.contacto
        } for e in empresas]

def exportar_excel(cliente, nombre_archivo=None):
    """Exporta todas las empresas del cliente a un archivo Excel."""
    if not nombre_archivo:
        nombre_archivo = f"{cliente}_empresas.xlsx"
    with get_session(cliente) as (session, engine):
        df = pd.read_sql(session.query(Empresa).statement, engine)
        # Limpieza básica para exportación
        for col in df.columns:
            df[col] = df[col].astype(str).str.strip()
        if "ID" in df.columns:
            df = df.rename(columns={"ID": "id"}, inplace=True)
        df.to_excel(nombre_archivo, index=False)
    print(f" Datos exportados a {nombre_archivo}")

def db_a_excel(cliente, ruta_destino):
    """Alias para exportar_excel, usado desde la interfaz."""
    try:
        exportar_excel(cliente, ruta_destino)
        return True
    except Exception as e:
        print(f" Error al exportar Excel: {e}")
        return False
    
def guardar_en_db(cliente, df):
    """Guarda múltiples empresas desde un DataFrame en la DB del cliente."""
    exitosos = 0
    for _, fila in df.iterrows():
        resultado = insertar_empresa(
            cliente,
            nombre=fila.get("nombre", ""),
            cuit=fila.get("cuit", ""),
            email=fila.get("email", ""),
            web=fila.get("web", ""),
            domicilio=fila.get("domicilio", ""),
            contacto=fila.get("contacto", "")
        )
        if resultado.get("ok"):
            exitosos += 1
    print(f" Guardadas {exitosos} empresas en {cliente}.db")
    return exitosos

def existe_empresa(cliente, nombre, cuit):
    """Verifica si ya existe una empresa con ese nombre o CUIT."""
    with get_session(cliente) as (session, _):
        return session.query(Empresa).filter(
            (Empresa.nombre == limpiar_texto(nombre)) |
            (Empresa.cuit == limpiar_texto(cuit))
        ).first() is not None