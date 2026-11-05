"""Generate demo data for LALA Desktop Application.

Creates:
1. sample_data/Listado_Participantes_Maestro.xlsx (Master participant reference dataset)
2. sample_data/SESION_Destino.xlsx (Target Excel workbook with previous session entries)
3. sample_data/formulario_manuscrito_simulado.png (Simulated handwritten form image)
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from PIL import Image, ImageDraw


def create_sample_files() -> None:
    output_dir = Path(__file__).resolve().parent
    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. Master Participants list
    master_data = [
        {"DNI": "12345678A", "NOMBRES": "JOSE", "1 APELLIDO": "MORALES", "2 APELLIDO": "CANAZO", "TELEFONO": "600111222", "EMAIL": "jose.morales@example.com"},
        {"DNI": "23456789B", "NOMBRES": "PEDRO", "1 APELLIDO": "PEREZ", "2 APELLIDO": "CARRASCOSA", "TELEFONO": "600222333", "EMAIL": "pedro.perez@example.com"},
        {"DNI": "34567890C", "NOMBRES": "PABLO", "1 APELLIDO": "SANCHEZ", "2 APELLIDO": "DEL VALLE", "TELEFONO": "600333444", "EMAIL": "pablo.sanchez@example.com"},
        {"DNI": "45678901D", "NOMBRES": "DAVID", "1 APELLIDO": "ZAMORA", "2 APELLIDO": "RUBIO", "TELEFONO": "600444555", "EMAIL": "david.zamora@example.com"},
        {"DNI": "56789012E", "NOMBRES": "JAVIER", "1 APELLIDO": "MORENO", "2 APELLIDO": "BORREGO", "TELEFONO": "600555666", "EMAIL": "javier.moreno@example.com"},
        {"DNI": "67890123F", "NOMBRES": "ANTONIO JESUS", "1 APELLIDO": "MARTIN", "2 APELLIDO": "RODRIGUEZ", "TELEFONO": "600666777", "EMAIL": "antonio.martin@example.com"},
        {"DNI": "78901234G", "NOMBRES": "DIEGO", "1 APELLIDO": "RODRIGUEZ", "2 APELLIDO": "BARBERAN", "TELEFONO": "600777888", "EMAIL": "diego.rodriguez@example.com"},
        {"DNI": "89012345H", "NOMBRES": "MANUEL JESUS", "1 APELLIDO": "GONZALEZ", "2 APELLIDO": "ALFARO", "TELEFONO": "600888999", "EMAIL": "manuel.gonzalez@example.com"},
        {"DNI": "90123456J", "NOMBRES": "MIGUEL ANGEL", "1 APELLIDO": "RODRIGUEZ", "2 APELLIDO": "LOPEZ", "TELEFONO": "600999000", "EMAIL": "miguel.rodriguez@example.com"},
        {"DNI": "01234567K", "NOMBRES": "SERGIO", "1 APELLIDO": "ESQUINAS", "2 APELLIDO": "LEDESMA", "TELEFONO": "600101010", "EMAIL": "sergio.esquinas@example.com"},
    ]
    df_master = pd.DataFrame(master_data)
    master_path = output_dir / "Listado_Participantes_Maestro.xlsx"
    df_master.to_excel(master_path, index=False, engine="openpyxl")
    print(f"Generated: {master_path}")

    # 2. Target Excel workbook with existing historical rows
    target_data = [
        {"DNI": "99988877X", "1 APELLIDO": "ALONSO", "2 APELLIDO": "GARCIA", "NOMBRE": "CARLOS", "OBSERVACIONES": "ASISTENCIA CONFIRMADA"},
        {"DNI": "88877766Y", "1 APELLIDO": "RAMOS", "2 APELLIDO": "HERRERA", "NOMBRE": "MARIA", "OBSERVACIONES": "ASISTENCIA CONFIRMADA"},
    ]
    df_target = pd.DataFrame(target_data)
    target_path = output_dir / "SESION_Destino.xlsx"
    df_target.to_excel(target_path, index=False, engine="openpyxl")
    print(f"Generated: {target_path}")

    # 3. Simulated handwritten form image
    img = Image.new("RGB", (1000, 600), color=(250, 250, 245))
    draw = ImageDraw.Draw(img)

    # Title
    draw.rectangle([(30, 30), (970, 90)], fill=(230, 235, 245), outline=(180, 190, 210), width=2)
    draw.text((50, 48), "HOJA DE ASISTENCIA Y REGISTRO MANUSCRITO - EVENTO LALA", fill=(30, 40, 60))

    # Grid headers
    col_x = [40, 300, 520, 740, 960]
    headers = ["NOMBRE COMPLETO", "DNI / IDENTIFICACION", "FIRMA", "OBSERVACIONES"]
    draw.rectangle([(40, 110), (960, 150)], fill=(220, 225, 235), outline=(160, 170, 190), width=1)

    for i, h in enumerate(headers):
        draw.text((col_x[i] + 10, 122), h, fill=(40, 50, 70))
        draw.line([(col_x[i], 110), (col_x[i], 550)], fill=(200, 205, 215), width=1)
    draw.line([(col_x[-1], 110), (col_x[-1], 550)], fill=(200, 205, 215), width=1)

    # Handwritten entries (simulated)
    simulated_entries = [
        ("Jose Morales Canazo", "", "[FIRMADO]", "TURNO MANANA"),
        ("Pedro Perez Carrascosa", "23456789B", "[FIRMADO]", "PUNTUAL"),
        ("Pablo Sanchez del Valle", "", "[FIRMADO]", "ASISTENTE"),
        ("David Zamora Rubio", "45678901D", "[FIRMADO]", "NUEVO INGRESO"),
        ("Antonio Jesus Martin Rodriguez", "", "[FIRMADO]", "JUSTIFICADO"),
    ]

    y_pos = 160
    for entry in simulated_entries:
        draw.rectangle([(40, y_pos), (960, y_pos + 60)], outline=(220, 220, 225), width=1)
        draw.text((col_x[0] + 15, y_pos + 18), entry[0], fill=(20, 30, 100))
        draw.text((col_x[1] + 15, y_pos + 18), entry[1], fill=(20, 30, 100))
        draw.text((col_x[2] + 15, y_pos + 18), entry[2], fill=(60, 70, 90))
        draw.text((col_x[3] + 15, y_pos + 18), entry[3], fill=(20, 30, 100))
        y_pos += 70

    img_path = output_dir / "formulario_manuscrito_simulado.png"
    img.save(img_path)
    print(f"Generated: {img_path}")


if __name__ == "__main__":
    create_sample_files()
