from datetime import datetime

def fecha_a_formato_legal(fecha):
    """
    Convierte datetime a formato legal con componentes separados
    con manejo robusto de errores y validación completa
    """
    # Diccionarios completos con valores por defecto
    dias = {
        1: 'uno', 2: 'dos', 3: 'tres', 4: 'cuatro', 5: 'cinco',
        6: 'seis', 7: 'siete', 8: 'ocho', 9: 'nueve', 10: 'diez',
        11: 'once', 12: 'doce', 13: 'trece', 14: 'catorce', 15: 'quince',
        16: 'dieciséis', 17: 'diecisiete', 18: 'dieciocho', 19: 'diecinueve', 
        20: 'veinte', 21: 'veintiuno', 22: 'veintidós', 23: 'veintitrés',
        24: 'veinticuatro', 25: 'veinticinco', 26: 'veintiséis', 
        27: 'veintisiete', 28: 'veintiocho', 29: 'veintinueve',
        30: 'treinta', 31: 'treinta y uno'
    }
    
    meses = {
        1: 'enero', 2: 'febrero', 3: 'marzo', 4: 'abril',
        5: 'mayo', 6: 'junio', 7: 'julio', 8: 'agosto',
        9: 'septiembre', 10: 'octubre', 11: 'noviembre', 12: 'diciembre'
    }
    
    try:
        # Validación robusta de la fecha
        if not isinstance(fecha, datetime):
            raise ValueError("Se esperaba un objeto datetime")
            
        if not (1 <= fecha.day <= 31):
            raise ValueError(f"Día {fecha.day} fuera de rango (1-31)")
            
        if not (1 <= fecha.month <= 12):
            raise ValueError(f"Mes {fecha.month} fuera de rango (1-12)")
        
        # Obtener representaciones con valores por defecto seguros
        dia_letras = dias.get(fecha.day, str(fecha.day)).upper()
        mes_letras = meses.get(fecha.month, str(fecha.month)).upper()
        
        # Conversión del año mejorada
        def convertir_año(año):
            # Diccionario completo para evitar errores de índice
            unidades = {
                0: 'CERO', 1: 'UNO', 2: 'DOS', 3: 'TRES', 4: 'CUATRO', 
                5: 'CINCO', 6: 'SEIS', 7: 'SIETE', 8: 'OCHO', 9: 'NUEVE',
                10: 'DIEZ', 11: 'ONCE', 12: 'DOCE', 13: 'TRECE', 14: 'CATORCE',
                15: 'QUINCE', 16: 'DIECISÉIS', 17: 'DIECISIETE', 18: 'DIECIOCHO',
                19: 'DIECINUEVE', 20: 'VEINTE', 21: 'VEINTIUNO', 22: 'VEINTIDÓS',
                23: 'VEINTITRÉS', 24: 'VEINTICUATRO', 25: 'VEINTICINCO',
                26: 'VEINTISÉIS', 27: 'VEINTISIETE', 28: 'VEINTIOCHO',
                29: 'VEINTINUEVE', 30: 'TREINTA', 31: 'TREINTA Y UNO',
                40: 'CUARENTA', 50: 'CINCUENTA', 60: 'SESENTA',
                70: 'SETENTA', 80: 'OCHENTA', 90: 'NOVENTA'
            }
            
            if not isinstance(año, int):
                return str(año)
                
            if 2000 <= año <= 2099:
                base = "DOS MIL "
                resto = año - 2000
                
                if resto in unidades:
                    return base + unidades[resto]
                else:
                    decena = (resto // 10) * 10
                    unidad = resto % 10
                    
                    # Validar que existan las claves necesarias
                    if decena in unidades and unidad in unidades:
                        if decena >= 20 and unidad > 0:
                            return base + unidades[decena] + " Y " + unidades[unidad]
                        return base + unidades[decena]
            
            return str(año)
        
        ano_letras = convertir_año(fecha.year)
        
        return {
            'completa': f"{dia_letras} ({fecha.day}) DE {mes_letras} DEL AÑO {ano_letras} ({fecha.year})",
            'dia': f"{dia_letras} ({fecha.day})",
            'mes': mes_letras,
            'ano_letras': ano_letras,
            'ano_numero': str(fecha.year),
            'ano_documento': f"{fecha.year} ({ano_letras.lower()})"
        }
    
    except Exception as e:
        print(f"Error al convertir fecha {fecha}: {str(e)}")
        # Retorna valores por defecto seguros
        return {
            'completa': f"[FECHA INVÁLIDA: {getattr(fecha, 'day', '?')}/{getattr(fecha, 'month', '?')}/{getattr(fecha, 'year', '?')}]",
            'dia': str(getattr(fecha, 'day', '?')),
            'mes': str(getattr(fecha, 'month', '?')),
            'ano_letras': str(getattr(fecha, 'year', '?')),
            'ano_numero': str(getattr(fecha, 'year', '?')),
            'ano_documento': str(getattr(fecha, 'year', '?'))
        }