import flet as ft
def gradient_button(*, text:str, width:int = 350, height:int = 48, gradient:list[ft.Colors], text_color:ft.Colors = ft.Colors.WHITE, on_click) -> ft.Container:
    return ft.Container(
        expand= False,
        width= width,
        height= height,
        gradient= ft.LinearGradient(
            begin=ft.alignment.center_left,
            end=ft.alignment.center_right,
            colors=gradient,
        ),
        border_radius=ft.border_radius.all(22),
        shadow=ft.BoxShadow(
            spread_radius=1,
            blur_radius=10,
            color=ft.Colors.with_opacity(0.3, ft.Colors.BLUE_GREY_900),
            offset=ft.Offset(0, 0),
        ),
        margin=ft.margin.only(top=20),
        content= ft.ElevatedButton(
            content= ft.Text(
                value= text,
                size= 20,
                color= text_color,
            ),
            expand=True,
            width= width,
            style= ft.ButtonStyle(
                bgcolor=ft.Colors.TRANSPARENT,
                overlay_color=ft.Colors.with_opacity(0.1, ft.Colors.WHITE),
                shadow_color=ft.Colors.TRANSPARENT,
                surface_tint_color=ft.Colors.TRANSPARENT,
            ),
            on_click= on_click
        )
    )