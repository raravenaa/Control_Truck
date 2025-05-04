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
            SELECT id, nombre, apellidos, rut, tipo_licencia, telefono, correo, sueldo_base, activo
            FROM conductores
            WHERE empresa_id = ?
            ORDER BY nombre
        """, (empresa_id,)).fetchall()

def agregar_conductor(empresa_id, nombre, apellidos, rut, tipo_licencia, telefono, correo, sueldo_base):
    with conexion() as conn:
        conn.execute("""
            INSERT INTO conductores (empresa_id, nombre, apellidos, rut, tipo_licencia, telefono, correo,sueldo_base, activo)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)
        """, (empresa_id, nombre, apellidos, rut, tipo_licencia, telefono, correo, sueldo_base))
        conn.commit()

def actualizar_conductor(id, nombre, apellidos, rut, tipo_licencia, telefono, correo, sueldo_base, activo):
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


# === DESTINOS ===
def obtener_destinos():
    with conexion() as conn:
        return conn.execute("""
            SELECT id, nombre, gasto_conductor, gasto_petroleo, valor_total, conductor
            FROM destinos
        """).fetchall()

def obtener_destinos_completos(empresa_id):
    with conexion() as conn:
        return conn.execute("""
            SELECT id, nombre, conductor, gasto_conductor, gasto_petroleo, valor_total, activo
            FROM destinos
            WHERE empresa = ?
            ORDER BY nombre
        """, (empresa_id,)).fetchall()

def guardar_destino(nombre, conductor_id, gasto_conductor, gasto_petroleo, valor_total):
    with conexion() as conn:
        conn.execute("""
            INSERT INTO destinos (nombre, conductor, gasto_conductor, gasto_petroleo, valor_total, activo)
            VALUES (?, ?, ?, ?, ?, 1)
        """, (nombre, conductor_id, gasto_conductor, gasto_petroleo, valor_total))
        conn.commit()

def actualizar_destino(id, nombre, conductor, gasto_conductor, gasto_petroleo, valor_total, activo):
    with conexion() as conn:
        conn.execute("""
            UPDATE destinos
            SET nombre = ?, conductor = ?, gasto_conductor = ?, gasto_petroleo = ?, valor_total = ?, activo = ?
            WHERE id = ?
        """, (nombre, conductor, gasto_conductor, gasto_petroleo, valor_total,activo, id))
        conn.commit()

def cambiar_estado_destino(destino_id, nuevo_estado):
    with conexion() as conn:
        conn.execute("""
            UPDATE destinos
            SET activo = ?
            WHERE id = ?
        """, (int(nuevo_estado), destino_id))
        conn.commit()

def crear_destino(nombre, gasto_conductor, gasto_petroleo, valor_total, conductor_id, empresa_id):
    with conexion() as conn:
        conn.execute("""
            INSERT INTO destinos (nombre, gasto_conductor, gasto_petroleo, valor_total, conductor, empresa, activo)
            VALUES (?, ?, ?, ?, ?, ?, 1)
        """, (nombre, gasto_conductor, gasto_petroleo, valor_total, conductor_id, empresa_id))



# === REGISTROS ===
def insertar_registro(data):
    with conexion() as conn:
        conn.execute("""
            INSERT INTO registros (
                empresa_id, conductor, fecha, numero_control, numero_guia, destino,
                gasto_conductor, gasto_petroleo, valor_total, id_estado
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, data)
        conn.commit()

def obtener_registros_por_empresa(empresa_id):
    with conexion() as conn:
        return conn.execute("""
            SELECT
                r.id, r.fecha, r.numero_control, r.numero_guia, r.destino,
                r.gasto_conductor, r.gasto_petroleo, r.valor_total,c.nombre as conductor,
                e.nombre AS estado
            FROM registros r
            JOIN estados e ON r.id_estado = e.id
            join conductores c ON r.conductor = c.id
            WHERE r.empresa_id = ?
            ORDER BY r.fecha DESC
        """,(empresa_id,)).fetchall()

def existe_numero_control(numero_control, empresa_id):
    with conexion() as conn:
        cursor = conn.execute("""
            SELECT 1 FROM registros
            WHERE numero_control = ? AND empresa_id = ?
            LIMIT 1
        """, (numero_control, empresa_id))
        return cursor.fetchone() is not None

def obtener_registros_rutas(empresa_id, fecha_inicio=None, fecha_fin=None):
    with conexion() as conn:
        if fecha_inicio and fecha_fin:
            return conn.execute("""
                SELECT
                    r.id, r.fecha AS fecha,
                    r.destino AS destino,
                    r.gasto_conductor, r.gasto_petroleo, r.valor_total,
                    c.id AS conductor_id,
                    c.nombre AS nombre_conductor,
                    c.rut,
                    c.sueldo_base
                FROM registros r
                JOIN conductores c ON r.conductor = c.id
                WHERE r.empresa_id = ?
                  AND r.fecha BETWEEN ? AND ?
                ORDER BY r.fecha DESC
            """, (empresa_id, fecha_inicio, fecha_fin)).fetchall()
        else:
            return conn.execute("""
                SELECT
                    r.id, r.fecha AS fecha,
                    r.destino AS destino,
                    r.gasto_conductor, r.gasto_petroleo, r.valor_total,
                    c.id AS conductor,
                    c.nombre AS nombre_conductor,
                    c.rut,
                    c.sueldo_base
                FROM registros r
                JOIN conductores c ON r.conductor = c.id
                WHERE r.empresa_id = ?
                ORDER BY r.fecha DESC
            """, (empresa_id,)).fetchall()