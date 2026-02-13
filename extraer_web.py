import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import json
from urllib.parse import urlparse

# Helpers para nombre (pegados del Step 1)
GENERIC_PATTERNS = [
    r"bienvenidos", r"ventas corporativas", r"home", r"inicio", r"oficial",
    r"contacto", r"tienda", r"env[ií]os?", r"servicio", r"atenci[oó]n", r"empresa",
    r"instituciones", r"canal exclusivo", r"comercializaci[oó]n", r"productos"
]

def limpiar_generico(texto):
    t = (texto or "").strip()
    if len(t) < 3:
        return ""
    if any(re.search(pat, t, flags=re.IGNORECASE) for pat in GENERIC_PATTERNS):
        return ""
    return t

def nombre_desde_url(url):
    host = urlparse(url).netloc.lower()
    host = re.sub(r"^(www|shop|store|tienda)\.", "", host)
    base = host.split(".")[0]
    base = re.sub(r"[-_]", " ", base).strip()
    nombre = base.title()
    nombre = nombre.replace("Fravega", "Frávega")
    return nombre

def extraer_nombre_empresa(sopa, url):
    nombre_url = nombre_desde_url(url)
    og_site = sopa.find("meta", attrs={"property": "og:site_name"})
    if og_site and og_site.get("content"):
        cand = limpiar_generico(og_site["content"])
        if cand and nombre_url.lower() in cand.lower():
            return cand
    app_name = sopa.find("meta", attrs={"name": "application-name"})
    if app_name and app_name.get("content"):
        cand = limpiar_generico(app_name["content"])
        if cand and nombre_url.lower() in cand.lower():
            return cand
    for script in sopa.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string or "")
            bloques = data if isinstance(data, list) else [data]
            for b in bloques:
                cand = limpiar_generico(str(b.get("name", "")))
                if cand:
                    return cand
        except Exception:
            pass
    posibles = [
        ("img", {"alt": True}),
        ("h1", {}),
        ("h2", {}),
        ("div", {"id": "site-branding"}),
        ("div", {"class": re.compile(r"logo|brand", re.I)}),
        ("a", {"class": re.compile(r"logo|brand", re.I)}),
    ]
    for tag, attrs in posibles:
        el = sopa.find(tag, attrs=attrs)
        if el:
            cand = limpiar_generico(el.get("alt") if tag == "img" else el.get_text(strip=True))
            if cand:
                if nombre_url.lower() in cand.lower():
                    return cand
                if len(cand.split()) <= 3:
                    return cand
    titulo = limpiar_generico(sopa.title.string.strip() if sopa.title and sopa.title.string else "")
    if titulo and nombre_url.lower() in titulo.lower():
        return titulo
    return nombre_url

def extraer_empresas_desde_web(url):
    try:
        respuesta = requests.get(url, timeout=10)
        sopa = BeautifulSoup(respuesta.text, "html.parser")

        emails = re.findall(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", sopa.text)
        telefonos = re.findall(r"\+?\d[\d\s\-\(\)]{7,}", sopa.text)

        nombre = extraer_nombre_empresa(sopa, url)

        datos = {
            "Nombre": nombre,
            "CUIT": "",
            "Email": emails[0] if emails else "",
            "web": url,
            "Domicilio": "",
            "Contacto": telefonos[0] if telefonos else ""
        }

        return pd.DataFrame([datos])
    except Exception as e:
        print("Error al extraer:", e)
        return None

