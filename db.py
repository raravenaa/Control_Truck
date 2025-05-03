# db.py
import sqlite3
from pathlib import Path

DB_PATH = Path("data/flota.db")


def conexion():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# === ESTADOS ===
def obtener_estados():
    with conexion() as conn:
        return conn.execute("SELECT id, nombre FROM estados").fetchall()


# === DESTINOS ===
def obtener_destinos():
    with conexion() as conn:
        return conn.execute("""
            SELECT id, nombre, gasto_conductor, gasto_petroleo, valor_total, conductor
            FROM destinos
        """).fetchall()


# === REGISTROS ===
def insertar_registro(data):
    with conexion() as conn:
        conn.execute('''
            INSERT INTO registros (
                empresa_id,conductor, fecha, numero_control, numero_guia, destino,
                gasto_conductor, gasto_petroleo, valor_total, id_estado
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', data)
        conn.commit()


def obtener_registros_por_empresa(empresa_id):
    with conexion() as conn:
        return conn.execute("""
            SELECT
                r.id, r.fecha, r.numero_control, r.numero_guia, r.destino,
                r.gasto_conductor, r.gasto_petroleo, r.valor_total,
                e.nombre AS estado
            FROM registros r
            JOIN estados e ON r.id_estado = e.id
            WHERE r.empresa_id = ?
            ORDER BY r.fecha DESC
        """, (empresa_id,)).fetchall()

def existe_numero_control(numero_control, empresa_id):
    with conexion() as conn:
        cursor = conn.execute("""
            SELECT 1 FROM registros
            WHERE numero_control = ? AND empresa_id = ?
            LIMIT 1
        """, (numero_control, empresa_id))
        return cursor.fetchone() is not None



def actualizar_estado_registro(registro_id, nuevo_estado_id):
    with conexion() as conn:
        conn.execute("""
            UPDATE registros SET id_estado = ? WHERE id = ?
        """, (nuevo_estado_id, registro_id))
        conn.commit()


# === CONDUCTORES ===
def obtener_conductores_por_empresa(empresa_id):
    with conexion() as conn:
        return conn.execute("""
            SELECT id, nombre,apellidos, rut,tipo_licencia, telefono, correo,sueldo_base, activo
            FROM conductores
            WHERE empresa_id = ? 
            ORDER BY nombre
        """, (empresa_id,)).fetchall()


def agregar_conductor(empresa_id, nombre, rut, telefono, correo ):
    with conexion() as conn:
        conn.execute("""
            INSERT INTO conductores (empresa_id, nombre, rut, telefono, correo, activo)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (empresa_id, nombre, rut, telefono, correo, 1 ))
        conn.commit()


def actualizar_conductor(id, nombre,apellidos, rut,tipo_licencia, telefono, correo,sueldo_base, activo):
    with conexion() as conn:
        conn.execute("""
            UPDATE conductores
            SET nombre = ?, apellidos = ?, rut = ?, tipo_licencia = ?, telefono = ?, correo = ?, sueldo_base = ?, activo = ?
            WHERE id = ?
        """, (nombre, apellidos, rut, tipo_licencia, telefono, correo, sueldo_base, activo, id))
        conn.commit()


def deshabilitar_conductor(conductor_id):
    with conexion() as conn:
        conn.execute("""
            UPDATE conductores
            SET activo = 0
            WHERE id = ?
        """, (conductor_id,))
        conn.commit()

