import flet as ft
from docx import Document
from docx.shared import Pt, Inches, Cm
import os
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT, WD_BREAK
from src.documents.formated_text import add_formatted_text
from src.documents.add_firm import add_firm
from src.app.functions.normalizar import es_venezolano, lista_con_y, normalizar_nacionalidad, normalizar_ocupaciones, normalizar_estados_civiles, imprimir_domicilios_unicos



def generate_constitutive_act(accionistas: list, presentante: dict, empresa: dict):
    try:
        doc = Document()
        
        style = doc.styles['Normal']
        style.font.name = 'Calibri' 
        style.font.size = Pt(14)
        
        section = doc.sections[0] 
        section.page_width = Inches(8.5)
        section.page_height = Inches(14)
        
        section.left_margin = Cm(3)
        section.right_margin = Cm(3)  
        section.top_margin = Cm(3)    
        section.bottom_margin = Cm(1.5)

        add_firm(doc)
        
        title = doc.add_paragraph()
        add_formatted_text(title, "CIUDADANO:\nREGISTRADOR MERCANTIL PRIMERO DE LA CIRCUNSCRIPCIÓN JUDICIAL DEL ESTADO ANZOATEGUI.\nSU DESPACHO:", bold=True)
        
        
        intro_p = doc.add_paragraph()
        add_formatted_text(intro_p, f"Yo, {presentante["nombre"].upper()}, ", bold=True)
        add_formatted_text(intro_p, f"{presentante["nacionalidad"]}, mayor de edad, {presentante["estado civil"]}, {presentante["ocupacion"]}, titular de la cédula de identidad personal No. {presentante["cedula"]}, con Registro de Información Fiscal (R.I.F) No. {presentante["rif"]} con domicilio en esta ciudad de {presentante["ciudad"]}, Municipio {presentante["municipio"]}, del Estado {presentante["estado"]}, debidamente")
        if presentante["nacionalidad"] == "venezolano":
            autorizado_text = "autorizado"
        else:
            autorizado_text = "autorizada"
        add_formatted_text(intro_p, f" {autorizado_text} en la presente acta de la compañía ")
        add_formatted_text(intro_p, f"\"COMPAÑIA PRUEBA, C.A \"", bold=True)
        add_formatted_text(intro_p, " empresa de este domicilio; Ante usted ocurro de conformidad con lo establecido en el Artículo 215 del Código de Comercio Vigente, para presentar el Documento Constitutivo de mi representada, el cual ha sido redactado con suficiente amplitud para que sirva de Estatutos de la misma. Participación que hago a Usted, a los fines de que, una vez cumplidos los trámites de inscripción, se sirva ordenar su Registro, Fijación y Publicación, con el ruego de expedirme sendas copias certificadas, de la presente participación del Documento Constitutivo, y del auto correspondiente. Es Justicia, que espero en esta ciudad a la fecha de su presentación. ")
        intro_p.alignment = WD_PARAGRAPH_ALIGNMENT.JUSTIFY
        
        
        firm = doc.add_paragraph()
        add_formatted_text(firm, "\n\n\n", bold=True)
        add_formatted_text(firm, f"\t\t\t\t\t\t{presentante["nombre"].upper()}\n\t\t\t\t\t\t\tC.I. {presentante["cedula"]}", bold=True)
        run = firm.add_run()
        run.add_break(WD_BREAK.PAGE)
        
        nombres_lista = [a["Nombre"] for a in accionistas]

        cedulas_lista = [
            f"{'V' if es_venezolano(a['Nacionalidad']) else 'E'}-{a['Cédula']}"
            for a in accionistas
        ]

        rif_lista = [
            a["RIF"] if a["RIF"].startswith("J-") else f"J-{a['RIF']}"
            for a in accionistas
        ]# evita duplicar J-

        
        nombres = lista_con_y(nombres_lista)
        cedulas = lista_con_y(cedulas_lista)
        rif = lista_con_y(rif_lista)
        nacionalidades = normalizar_nacionalidad(accionistas)
        ocupaciones = normalizar_ocupaciones(accionistas)   
        estado = normalizar_estados_civiles(accionistas)
        domicilio = imprimir_domicilios_unicos(accionistas)
        # impre
        add_firm(doc)
        title2 = doc.add_paragraph()
        add_formatted_text(title2, "DOCUMENTO CONSTITUTIVO EMPRESA\n\"COMPAÑIA PRUEBA, C.A\"", bold=True)
        title2.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
        
        
        text_2 = doc.add_paragraph()
        add_formatted_text(text_2, " Nosotros, ")
        add_formatted_text(text_2, f"{nombres.upper()}", bold=True)
        add_formatted_text(text_2, f"{nacionalidades}, mayores de edad, {ocupaciones}, de estado civil {estado}, titulares de la cédula de identidad personal numeros: {cedulas}, con Registro de Información Fiscal (R.I.F) número: {rif}, respectivamente con domicilio en {domicilio}; por medio del presente documento declaramos: Que hemos convenido en constituir como en efecto constituimos una Compañía Anónima, la cual se regirá por las Cláusulas contenidas en el presente documento:")
        text_2.alignment = WD_PARAGRAPH_ALIGNMENT.JUSTIFY
        
        title_cap2 = doc.add_paragraph()
        add_formatted_text(title_cap2, "CAPÍTULO I:\nDENOMINACIÓN, OBJETO, DOMICICLIO Y DURACIÓN.", bold=True)
        title2.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
        
        cap1 = doc.add_paragraph()
        add_formatted_text(cap1, "PRIMERA: ", bold=True)
        add_formatted_text(cap1, f"la compañía se denominará \"{empresa["Nombre"]}\".\n")
        add_formatted_text(cap1, "SEGUNDA: ", bold=True)
        add_formatted_text(cap1, f"La compañía tendrá como objeto principa {empresa["Dedicación"]} y en fin cualquier actividad que esté relacionada o conexa con el objeto principal, dentro y fuera del país. ")
        add_formatted_text(cap1, "TERCERA: ", bold=True)
        add_formatted_text(cap1, "La compañía tendrá domicilio en ")
        add_formatted_text(cap1, f"la ciudad de {empresa["Domicilio (Ciudad)"]}, Municipio {empresa["Domicilio (Municipio)"]} del Estado {empresa["Domicilio (Estado)"]}.".upper())
        add_formatted_text(cap1, "pudiendo establecer Agencias, Oficinas y/o sucursales en cualquier lugar de la República Bolivariana de Venezuela o el exterior. ")
        add_formatted_text(cap1, "CUARTA: ", bold=True)
        add_formatted_text(cap1, f"La duración de la compañía será de un ({empresa["Duración"]}) años, contados a partir de la fecha de su Inscripción por ante la Oficina de Registro Mercantil competente.")
        cap1.alignment = WD_PARAGRAPH_ALIGNMENT.JUSTIFY
    
        cap2 = doc.add_paragraph()
        add_formatted_text(cap2, "QUINTA: ", bold=True)
        add_formatted_text(cap2, "El capital de la Compañía es de")    
        
        
        
        
        
        
        
        documents_path = os.path.join(os.path.expanduser("~"), "Documents")
        manager_path = os.path.join(documents_path, "Axiology Document Manager")
        contracts_path = os.path.join(manager_path, "Contratos Generados")
        sales_path = os.path.join(contracts_path, "Actas Constitutivas")
        os.makedirs(sales_path, exist_ok=True)
        
        base = "ACTA CONSTITUTIVA"
        cont = 1
        filename =  f"{base}.docx"
    
        while os.path.exists(os.path.join(sales_path, filename)):
            filename = f"{base} ({cont}).docx"
            cont += 1
        
        full_path = os.path.join(sales_path, filename)
        doc.save(full_path)
        return full_path
    except Exception as e:
            print(f"Error al generar el documento: {e}")
            return None