import flet as ft
from docx import Document
from docx.shared import Pt, Inches, Cm
import os
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT, WD_BREAK
from src.documents.formated_text import add_formatted_text
from src.documents.add_firm import add_firm

def generate_constitutive_act(accionistas: list, presentante: dict):
    
    nombres = ", ".join(a["Nombre"] for a in accionistas)
    cedulas = ", ".join(a["Cédula"] for a in accionistas)
    
    texto = (
        f"Nosotros: {nombres}, titulares de la cédula de identidad {cedulas}, "
        "declaramos ante el Tribunal Supremo de Justicia..."
    )

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
        add_formatted_text(title, "CIUDADANO\nREGISTRADOR MERCANTIL PRIMERO DE LA CIRCUNSCRIPCIÓN JUDICIAL DEL ESTADO ANZOATEGUI.\nSU DESPACHO:", bold=True)
        
        
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
        
        add_firm(doc)
        title2 = doc.add_paragraph()
        add_formatted_text(title2, "DOCUMENTO CONSTITUTIVO EMPRESA\n\"COMPAÑIA PRUEBA, C.A\"", bold=True)
        title2.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
        
        
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