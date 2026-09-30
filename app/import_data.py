import pandas as pd
import sqlite3

# Conexión a la base de datos
conn = sqlite3.connect('inventario.db')

# Leer el archivo excel, ignorando las primeras 4 filas que son encabezados
df = pd.read_excel('/app/ELABORACIÓN_DE_PRODUCTOS_CON_CONTROL_DE_DESCARTES_CORREGIDO.xlsx', skiprows=4, header=None)

# Mapear las columnas a los nombres de la base de datos
# 0: FECHA ELABORACIÓN
# 1: PRODUCTO
# 2: NÚMERO ORDEN DE FABRICACIÓN
# 3: CANTIDAD (g)
# 4: FECHA DE DESCARTE
# 5: CANTIDAD PRODUCTO (Kg-L)
# 6: TEMPERATURA FINAL DE COCCIÓN (°C)
# 7: HORA INICIAL ENFRIAMIENTO
# 8: HORA FINAL ENFRIAMIENTO
# 9: TIEMPO TOTAL ENFRIAMIENTO
# 10: TEMPERATURA ENFRIAMIENTO FINAL (°C)
# 11: Nro. TERMÓMETRO
# 12: RESPONSABLE ELABORACIÓN
# 13: SABOR
# 15: OLOR
# 17: COLOR
# 19: TEXTURA
# 21: RESPONSABLE SENSORIAL
# 22: OBSERVACIÓN

column_map = {
    0: 'fecha_elaboracion',
    1: 'producto',
    2: 'numero_orden',
    3: 'cantidad_muestra',
    4: 'fecha_descarte',
    5: 'cantidad_producto',
    6: 'temperatura_coccion',
    7: 'hora_inicial_enfriamiento',
    8: 'hora_final_enfriamiento',
    9: 'tiempo_total_enfriamiento',
    10: 'temperatura_final_enfriamiento',
    11: 'nro_termometro',
    12: 'responsable_elaboracion',
    13: 'sabor',
    15: 'olor',
    17: 'color',
    19: 'textura',
    21: 'responsable_sensorial',
    22: 'observacion'
}

# Filtrar solo las columnas mapeadas y renombrarlas
df_mapped = df[list(column_map.keys())].rename(columns=column_map)

# Limpiar los datos
# Convertir fechas a formato string para SQLite (YYYY-MM-DD)
for col in ['fecha_elaboracion', 'fecha_descarte']:
    df_mapped[col] = pd.to_datetime(df_mapped[col], errors='coerce').dt.strftime('%Y-%m-%d')

# Convertir tiempos a string
for col in ['hora_inicial_enfriamiento', 'hora_final_enfriamiento']:
    df_mapped[col] = df_mapped[col].astype(str).replace('nan', None)

# Filtrar filas vacías (donde producto es nulo)
df_clean = df_mapped.dropna(subset=['producto'])

# Insertar en la base de datos
df_clean.to_sql('muestras', conn, if_exists='append', index=False)

print(f"Importadas {len(df_clean)} filas.")
conn.close()
