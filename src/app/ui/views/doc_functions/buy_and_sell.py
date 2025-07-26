import flet as ft
from docx import Document
import pandas as pd
import os
from datetime import datetime

def compraventa_contract_view(page: ft.Page):
    # Listas para guardar los campos y poder acceder a sus valores después
    vendedor_fields = []
    comprador_fields = []
    inmueble_fields = []
    oficina_fields = []

    # Crea un TextField y lo guarda en la lista correspondiente
    def crear_input(label, lista):
        campo = ft.TextField(label=label, filled=True, expand=True)
        lista.append(campo)
        return campo

    def crear_seccion(titulo, campos, lista_destino):
        return ft.Column([
            ft.Text(titulo, style=ft.TextThemeStyle.HEADLINE_MEDIUM, weight="bold"),
            ft.ResponsiveRow(
                [crear_input(campo, lista_destino) for campo in campos],
                columns=12,
                alignment="start",
                spacing=10
            )
        ], spacing=15)

    vendedor_campos = [
        "Nombre", "Nacionalidad", "Ocupación", "Estado civil", 
        "Cédula", "RIF", "Domicilio (Ciudad)", "Domicilio (Municipio)", "Domicilio (Estado)"
    ]

    comprador_campos = [
        "Nombre", "Nacionalidad", "Estado civil", "RIF",
        "Domicilio (Ciudad)", "Domicilio (Municipio)", "Domicilio (Estado)"
    ]

    inmueble_campos = [
        "Razón (Edificio/Casa/Apartamento)", "Domicilio (Ciudad)", "Domicilio (Municipio)", "Domicilio (Estado)",
        "Código catastral", "Superficie (m²)",
        "Límite Norte", "Límite Sur", "Límite Este", "Límite Oeste",
        "Precio", "Número de cheque", "Cuenta a depositar", "Banco"
    ]

    oficina_campos = [
        "Domicilio (Ciudad)", "Domicilio (Municipio)", "Domicilio (Estado)",
        "Fecha", "Número de folio", "Protocolo", "Tomo", "Trimestre referido"
    ]

    def generar_contrato(e):
        # Aquí puedes usar los .value de los campos
        datos = {
            "vendedor": {campo.label: campo.value for campo in vendedor_fields},
            "comprador": {campo.label: campo.value for campo in comprador_fields},
            "inmueble": {campo.label: campo.value for campo in inmueble_fields},
            "oficina": {campo.label: campo.value for campo in oficina_fields},
        }

        # Solo mostramos en consola por ahora
        print("Datos capturados:")
        for seccion, valores in datos.items():
            print(f"--- {seccion.upper()} ---")
            for k, v in valores.items():
                print(f"{k}: {v}")

        # Aquí puedes generar el .docx con los datos si lo deseas 💍

    return ft.Column(
        controls=[
            ft.Column([
                crear_seccion("Datos del Vendedor", vendedor_campos, vendedor_fields),
                crear_seccion("Datos del Comprador", comprador_campos, comprador_fields),
                crear_seccion("Datos del Inmueble", inmueble_campos, inmueble_fields),
                crear_seccion("Datos de Oficina", oficina_campos, oficina_fields),
                ft.ElevatedButton("Generar Contrato", icon=ft.Icons.DESCRIPTION, on_click=generar_contrato),
                ft.Container(height=100)
            ], spacing=15, scroll=ft.ScrollMode.AUTO, expand=True)
        ],
        height=600,
        expand=True,
        width=800,
    )
