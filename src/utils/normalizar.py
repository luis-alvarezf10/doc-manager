def normalizar_nacionalidad(accionistas):
    # Diccionario de singular/plural para cada nacionalidad por género
    nacionalidades_dict = {
        "venezolano": ("Venezolano", "Venezolana", "Venezolanos", "Venezolanas"),
        "Portugués": ("Portugués", "Portuguesa", "Portugueses", "Portuguesas"),
        "árabe": ("Árabe", "Árabe", "Árabes", "Árabes"),
        "italiano": ("Italiano", "Italiana", "Italianos", "Italianas"),
        "español": ("Español", "Española", "Españoles", "Españolas"),
        "líbanes": ("líbanes", "líbanesa", "líbaneses", "líbanesas"),
        "turco": ("Turco", "Turca", "Turcos", "Turcas"),
        "chino": ("Chino", "China", "Chinos", "Chinas"),
        "español": ("español", "española", "españoles", "españolas"),
        "alemán": ("Alemán", "Alemana", "Alemanes", "Alemanas"),
        "francés": ("Francés", "Francesa", "Franceses", "Francesas")
    }

    conteo = {}

    for a in accionistas:
        nac = a["Nacionalidad"].lower()
        sexo = a["Sexo"].lower()

        if nac not in conteo:
            conteo[nac] = {"masculino": 0, "femenino": 0}

        conteo[nac][sexo] += 1

    frases = []

    for nac, sexos in conteo.items():
        if nac not in nacionalidades_dict:
            continue  # ignorar nacionalidades desconocidas

        masc, fem = sexos["masculino"], sexos["femenino"]
        sing_m, sing_f, plural_m, plural_f = nacionalidades_dict[nac]

        if masc + fem == 1:
            frase = sing_f if fem == 1 else sing_m
        else:
            if fem == 0:
                frase = plural_m
            elif masc == 0:
                frase = plural_f
            else:
                frase = plural_m  # forma neutra en masculino plural
        frases.append(frase)

    # Unir con "y" o "e" correctamente
    if len(frases) > 1:
        if frases[-1][0].lower() in "ei":
            texto = ", ".join(frases[:-1]) + " e " + frases[-1]
        else:
            texto = ", ".join(frases[:-1]) + " y " + frases[-1]
    else:
        texto = frases[0] if frases else ""

    return texto

def normalizar_ocupaciones(accionistas):
    ocupaciones = {}

    for a in accionistas:
        sexo = a["Sexo"].lower()
        genero = "femenino" if "fem" in sexo else "masculino"
        ocupacion = a["Ocupación"].strip().lower()

        if ocupacion not in ocupaciones:
            ocupaciones[ocupacion] = {"masculino": 0, "femenino": 0}
        ocupaciones[ocupacion][genero] += 1

    resultado = []

    for ocupacion, conteo in ocupaciones.items():
        masc = conteo["masculino"]
        fem = conteo["femenino"]

        if masc > 0 and fem > 0:
            plural = pluralizar_ocupacion(ocupacion)
        elif masc > 1:
            plural = pluralizar_ocupacion(ocupacion)
        elif fem > 1:
            plural = pluralizar_ocupacion(ocupacion, femenino=True)
        elif fem == 1:
            plural = capitalizar(ocupacion, femenino=True)
        else:
            plural = capitalizar(ocupacion)
        
        resultado.append(plural)

    return unir_con_y(resultado)


def pluralizar_ocupacion(ocupacion, femenino=False):
    # reglas básicas de pluralización (puedes mejorarlas)
    base = ocupacion
    if ocupacion.endswith("a") and not ocupacion.endswith("ista"):
        return base + "s" if femenino else base[:-1] + "os"
    elif ocupacion.endswith("o"):
        return base[:-1] + ("os" if not femenino else "as")
    elif ocupacion.endswith("e") or ocupacion.endswith("ista"):
        return base + "s"
    else:
        return base + "es"


def capitalizar(ocupacion, femenino=False):
    # cambia "abogado" → "Abogada" si femenino
    if femenino and ocupacion.endswith("o"):
        ocupacion = ocupacion[:-1] + "a"
    return ocupacion.capitalize()


def unir_con_y(lista):
    if len(lista) > 2:
        return ", ".join(lista[:-1]) + " y " + lista[-1]
    elif len(lista) == 2:
        return " y ".join(lista)
    elif lista:
        return lista[0]
    return ""


def normalizar_estados_civiles(accionistas):
    estados = {}

    for a in accionistas:
        sexo = a["Sexo"].lower()
        genero = "femenino" if "fem" in sexo else "masculino"
        estado = a["Estado civil"].strip().lower().replace("/a", "")  # Soltero/a → soltero

        if estado not in estados:
            estados[estado] = {"masculino": 0, "femenino": 0}
        estados[estado][genero] += 1

    resultado = []

    for estado, conteo in estados.items():
        masc = conteo["masculino"]
        fem = conteo["femenino"]

        if masc > 0 and fem > 0:
            plural = pluralizar_estado(estado)
        elif masc > 1:
            plural = pluralizar_estado(estado)
        elif fem > 1:
            plural = pluralizar_estado(estado, femenino=True)
        elif fem == 1:
            plural = capitalizar_estado(estado, femenino=True)
        else:
            plural = capitalizar_estado(estado)
        
        resultado.append(plural)

    return unir_con_y(resultado)


def pluralizar_estado(estado, femenino=False):
    # Casado → Casados / Casadas
    if estado.endswith("o"):
        return estado[:-1] + ("as" if femenino else "os")
    return estado + "s"  # fallback

def capitalizar_estado(estado, femenino=False):
    if femenino and estado.endswith("o"):
        estado = estado[:-1] + "a"
    return estado.capitalize()

def unir_con_y(lista):
    if len(lista) > 2:
        return ", ".join(lista[:-1]) + " y " + lista[-1]
    elif len(lista) == 2:
        return " y ".join(lista)
    elif lista:
        return lista[0]
    return ""
def imprimir_domicilios_unicos(accionistas):
    domicilios_unicos = []
    
    for a in accionistas:
        domicilio = (
            a["Domicilio (Ciudad)"],
            a["Domicilio (Municipio)"],
            a["Domicilio (Estado)"]
        )
        if domicilio not in domicilios_unicos:
            domicilios_unicos.append(domicilio)

    partes = [
        f"la ciudad de {ciudad}, Jurisdicción del Municipio {municipio} del Estado {estado}"
        for ciudad, municipio, estado in domicilios_unicos
    ]

    # Unir con comas y “y” al final, si hay más de un domicilio
    if len(partes) > 1:
        texto = ", ".join(partes[:-1]) + " y " + partes[-1]
    else:
        texto = partes[0]

    return texto

def lista_con_y(lista):
    if len(lista) > 2:
        return ", ".join(lista[:-1]) + " y " + lista[-1]
    elif len(lista) == 2:
        return " y ".join(lista)
    elif lista:
        return lista[0]
    else:
        return ""

    
def es_venezolano(nac):
    return nac.strip().lower().startswith("vene")


def normalizar_acciones(accionistas, nomina):
    """Normaliza la descripción de acciones suscritas por cada accionista"""
    from src.utils.convert_to_letters import number_to_letters
    
    descripciones = []
    
    for i, accionista in enumerate(accionistas):
        nombre = accionista["Nombre"].upper()
        no_acciones = int(accionista["No Acciones"])
        valor_total = nomina * no_acciones
        
        # Convertir número de acciones a letras
        try:
            acciones_letras = number_to_letters(no_acciones, incluir_moneda=False)
            valor_total_text = number_to_letters(valor_total)
        except:
            acciones_letras = "[Error al convertir]"
        
        base = f"{nombre}, ha suscrito y pagado {acciones_letras} ({no_acciones}) acciones, por un valor de {valor_total_text} (Bs. {valor_total:.2f})"
        # Formato según posición
        if i == 0:
            descripcion = base
        else:
            descripcion = f"el socio: {base}" 
            
        descripciones.append(descripcion)
    
    return "; ".join(descripciones) + "."

def pluralizar_cargo(cargo):
    """Pluraliza un cargo individual"""
    cargo_lower = cargo.lower()
    
    plurales = {
        "presidente": "presidentes",
        "vicepresidente": "vicepresidentes", 
        "secretario": "secretarios",
        "tesorero": "tesoreros",
        "miembro": "miembros",
        "suplente": "suplentes",
        "director general": "directores generales",
        "director administrativo": "directores administrativos",
        "director ejecutivo": "directores ejecutivos",
        "gerente general": "gerentes generales",
        "gerente administrativo": "gerentes administrativos",
        "gerente de finanzas": "gerentes de finanzas",
        "gerente de operaciones": "gerentes de operaciones",
        "asesor legal": "asesores legales",
        "asesor financiero": "asesores financieros",
        "comisario": "comisarios",
        "auditor interno": "auditores internos",
        "vocal": "vocales",
        "representante legal": "representantes legales",
        "socio fundador": "socios fundadores",
        "consejero": "consejeros"
    }
    
    return plurales.get(cargo_lower, cargo + "s").upper()

def normalizar_cargos(accionistas):
    """Normaliza los cargos de los accionistas"""
    from src.utils.convert_to_letters import number_to_letters
    
    cargos = {}
    for a in accionistas:
        cargo = a["Cargo"].strip()
        if cargo not in cargos:
            cargos[cargo] = 0
        cargos[cargo] += 1
    
    # Obtener el cargo más común
    if cargos:
        cargo_principal = max(cargos, key=cargos.get)
        cargo_plural = pluralizar_cargo(cargo_principal)
    else:
        cargo_plural = "DIRECTORES GENERALES"
    
    cantidad = len(accionistas)
    
    try:
        cantidad_letras = number_to_letters(cantidad, incluir_moneda=False)
    except:
        cantidad_letras = "[Error]"
    
    return {
        "cantidad": cantidad,
        "cantidad_letras": cantidad_letras,
        "cargo_principal": cargo_plural
    }

def normalizar(accionistas):
    """Función principal que normaliza nacionalidades y ocupaciones de accionistas"""
    nacionalidades = normalizar_nacionalidad(accionistas)
    ocupaciones = normalizar_ocupaciones(accionistas)
    return {
        "nacionalidades": nacionalidades,
        "ocupaciones": ocupaciones
    }
