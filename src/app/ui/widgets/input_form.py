import flet as ft

input_list = []
def create_input(titulo: None, label, lista):
    def _move_focus(e):
        current_index = next((i for i, control in enumerate(input_list) if control == e.control), -1)
        if current_index != -1 and current_index + 1 < len(input_list):
            input_list[current_index + 1].focus()
        e.page.update()

    label_lower = label.lower()

    # Dropdowns
    if label_lower in ["estado civil", "razón", "trimestre referido"]:
        options_dict = {
            "estado civil": ["Soltero/a", "Casado/a", "Divorciado/a", "Viudo/a"],
            "Tipo de Inmueble": ["Edificio", "Casa", "Apartamento", "Terreno", "Local Comercial"],
            "trimestre referido": ["Primer", "Segundo", "Tercer", "Cuarto"]
        }

        dropdown = ft.Dropdown(
            label=label,
            options=[ft.dropdown.Option(opt) for opt in options_dict[label_lower]],
            filled=True,
            expand=True,
            border_radius=8,
            border_width=0,
            border_color="transparent",
            focused_border_width=0,
            text_size=16,
            on_change=_move_focus,
        )
        input_list.append(dropdown)
        if isinstance(lista, dict):
            lista[label] = dropdown
        elif isinstance(lista, list):
            lista.append(dropdown)
        return dropdown

    # TextField con valor predeterminado
    if titulo.lower() == "datos de oficina" and label_lower in ["domicilio (ciudad)", "domicilio (municipio)", "domicilio (estado)"]:
        default_values = {
            "domicilio (ciudad)": "Barcelona",
            "domicilio (municipio)": "Simón Bolívar",
            "domicilio (estado)": "Anzoátegui"
        }
        tf = ft.TextField(
            label=label,
            value=default_values.get(label_lower, ""),
            filled=True,
            expand=True,
            border_radius=8,
            border_width=0,
            border_color="transparent",
            focused_border_width=0,
            text_size=16,
            on_submit=_move_focus,
        )
        input_list.append(tf)
        if isinstance(lista, dict):
            lista[label] = tf
        elif isinstance(lista, list):
            lista.append(tf)
        return tf
    if titulo.lower() == "datos de accionista" and label_lower == "ocupación":
        tf = ft.TextField(
            label=label,
            value= "comerciante",
            filled=True,
            expand=True,
            border_radius=8,
            border_width=0,
            border_color="transparent",
            focused_border_width=0,
            text_size=16,
            on_submit=_move_focus,
        )
        input_list.append(tf)
        if isinstance(lista, dict):
            lista[label] = tf
        elif isinstance(lista, list):
            lista.append(tf)
        return tf
    if label_lower == "nacionalidad":
        tf = ft.TextField(
            label=label,
            value="venezolano/a",
            filled=True,
            expand=True,
            border_radius=8,
            border_width=0,
            border_color="transparent",
            focused_border_width=0,
            text_size=16,
            on_submit=_move_focus,
        )
        input_list.append(tf)
        if isinstance(lista, dict):
            lista[label] = tf
        elif isinstance(lista, list):
            lista.append(tf)
        return tf
    # TextField general
    tf = ft.TextField(
        label=label,
        filled=True,
        expand=True,
        border_radius=8,
        border_width=0,
        border_color="transparent",
        focused_border_width=0,
        text_size=16,
        on_submit=_move_focus,
    )
    input_list.append(tf)
    if isinstance(lista, dict):
        lista[label] = tf
    elif isinstance(lista, list):
        lista.append(tf)
    return tf
