from docx.enum.text import WD_UNDERLINE

def add_formatted_text(paragraph, text, bold=False, underline=False):
    run = paragraph.add_run(text)
    run.bold = bold
    if underline:
        run.underline = WD_UNDERLINE.SINGLE
    return paragraph
