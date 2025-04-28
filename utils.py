# utils.py

def formato_clp(valor):
    """Formatea un número como peso chileno sin decimales."""
    if valor is None:
        return "-"
    try:
        return f"${int(valor):,}".replace(",", ".")
    except (ValueError, TypeError):
        return str(valor)

def generar_tabla_coloreada(df, colores_estado):
    def color_fila(estado):
        return colores_estado.get(estado.lower(), "#FFFFFF")  # Blanco por defecto

    html = """
    <style>
        .styled-table {{
            width: 100%;
            border-collapse: collapse;
        }}
        .styled-table th, .styled-table td {{
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }}
    </style>
    <table class="styled-table">
        <thead>
            <tr>{}</tr>
        </thead>
        <tbody>
    """.format("".join(f"<th>{col}</th>" for col in df.columns))

    for _, row in df.iterrows():
        color = color_fila(row["estado"])
        html += f'<tr style="background-color:{color}">'
        html += "".join(f"<td>{row[col]}</td>" for col in df.columns)
        html += "</tr>"

    html += "</tbody></table>"
    return html
