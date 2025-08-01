from docx.shared import Pt
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT

def add_firm(doc):
    impre = doc.add_paragraph()
    runs = [
        ("PEDRO LUIS ALVAREZ", True),
        ("ABOGADO", True),
        ("I.P.S.A: 41.432", False)
    ]
    for text, add_break in runs:
        run = impre.add_run(text)
        run.font.size = Pt(9)
        run.font.name = "Algerian"
        if add_break:
            run.add_break() 
    impre.alignment = WD_PARAGRAPH_ALIGNMENT.LEFT