# db.py
import sqlite3
from pathlib import Path

DB_PATH = Path("data/flota.db")

def conexion():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Para acceder a columnas por nombre
    return conn

def obtener_estados():
    conn = conexion()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre FROM estados")
    estados = cursor.fetchall()
    conn.close()
    return estados

def obtener_destinos():
    conn = conexion()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre, gasto_conductor, gasto_petroleo, valor_total FROM destinos")
    destinos = cursor.fetchall()
    conn.close()
    return destinos

def insertar_registro(data):
    conn = conexion()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO registros (
            empresa_id, fecha, numero_control, numero_guia, destino,
            gasto_conductor, gasto_petroleo, valor_total, id_estado
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', data)
    conn.commit()
    conn.close()

def obtener_registros_por_empresa(empresa_id):
        conn = conexion()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                r.id,
                r.fecha,
                r.numero_control,
                r.numero_guia,
                r.destino,
                r.gasto_conductor,
                r.gasto_petroleo,
                r.valor_total,
                e.nombre AS estado
            FROM registros r
            JOIN estados e ON r.id_estado = e.id
            WHERE r.empresa_id = ?
            ORDER BY r.fecha DESC
        """, (empresa_id,))
        rows = cursor.fetchall()
        conn.close()
        return rows

def actualizar_estado_registro(registro_id, nuevo_estado_id):
    conn = conexion()
    cursor = conn.cursor()
    cursor.execute("UPDATE registros SET id_estado = ? WHERE id = ?", (nuevo_estado_id, registro_id))
    conn.commit()
    conn.close()
