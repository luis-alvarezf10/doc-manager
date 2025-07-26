import flet as ft

def gradient_text(*, text:str, text_weight:ft.FontWeight = ft.FontWeight.BOLD, size:int, gradient:list[ft.Colors]) -> ft.ShaderMask:
    return ft.ShaderMask(
        content= ft.Text(
            text,
            size=size,
            weight=text_weight,
            color= ft.Colors.WHITE,
            text_align= ft.TextAlign.CENTER,
        ),
        blend_mode= ft.BlendMode.SRC_IN,
        shader= ft.LinearGradient(
            colors=gradient,
            begin= ft.alignment.top_left,
            end= ft.alignment.bottom_right,
        ),
    )