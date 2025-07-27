def number_to_letters(numero, moneda="bolívares", incluir_moneda=True, es_metros_cuadrados=False):
    """
    Función corregida para convertir números a letras correctamente, incluyendo casos como 1.000.099,50
    """
    def convertir_entero(n):
        """Convierte números enteros a letras (0-999.999.999) correctamente."""
        unidades = ["", "un", "dos", "tres", "cuatro", "cinco", "seis", "siete", "ocho", "nueve"]
        especiales = ["diez", "once", "doce", "trece", "catorce", "quince", "dieciséis", "diecisiete", "dieciocho", "diecinueve"]
        decenas = ["veinte", "treinta", "cuarenta", "cincuenta", "sesenta", "setenta", "ochenta", "noventa"]
        centenas = ["", "ciento", "doscientos", "trescientos", "cuatrocientos", "quinientos", "seiscientos", "setecientos", "ochocientos", "novecientos"]

        if n == 0:
            return "cero"
        if n == 100:
            return "cien"

        texto = []
        # Millones
        if n >= 1_000_000:
            millon = n // 1_000_000
            texto.append("un millón" if millon == 1 else f"{convertir_entero(millon)} millones")
            n %= 1_000_000
        # Miles
        if n >= 1_000:
            mil = n // 1_000
            texto.append("mil" if mil == 1 else f"{convertir_entero(mil)} mil")
            n %= 1_000
        # Centenas
        if n >= 100:
            centena = n // 100
            texto.append("cien" if centena == 1 and n % 100 == 0 else centenas[centena])
            n %= 100
        # Decenas y unidades
        if 10 <= n < 20:
            texto.append(especiales[n - 10])
        elif n == 20:
            texto.append("veinte")
        elif 20 < n < 30:
            texto.append(f"veinti{unidades[n % 10]}")
        elif n >= 30:
            decena = decenas[(n // 10) - 2]
            if n % 10 == 0:
                texto.append(decena)
            else:
                texto.append(f"{decena} y {unidades[n % 10]}")
        elif n > 0:
            texto.append(unidades[n])

        return " ".join(texto).replace("veintiun", "veintiuno")

    try:
        # Limpieza del número
        if isinstance(numero, str):
            numero = numero.replace(".", "").replace(",", ".")
        numero = float(numero)

        entero = int(numero)
        decimal = round((numero - entero) * 100)

        texto_entero = convertir_entero(entero).upper()
        texto_decimal = convertir_entero(decimal).upper() if decimal > 0 else None

        # Formateo final
        resultado = texto_entero
        if incluir_moneda and not es_metros_cuadrados:
            resultado += f" {moneda.upper()}"
        if decimal > 0:
            resultado += f" CON {texto_decimal} CÉNTIMOS"
        if es_metros_cuadrados:
            resultado += " METROS CUADRADOS"

        return resultado

    except Exception as e:
        return f"[ERROR: {str(e)}]"