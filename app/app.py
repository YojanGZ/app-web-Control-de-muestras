import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, date

st.title('Sistema de Inventario de Muestras')

# Conexión a la base de datos
conn = sqlite3.connect('inventario.db')
c = conn.cursor()

# Crear tabla si no existe
c.execute('''
    CREATE TABLE IF NOT EXISTS muestras (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha_elaboracion DATE,
        producto TEXT,
        numero_orden TEXT,
        cantidad_muestra REAL,
        fecha_descarte DATE,
        cantidad_producto REAL,
        temperatura_coccion REAL,
        hora_inicial_enfriamiento TEXT,
        hora_final_enfriamiento TEXT,
        tiempo_total_enfriamiento TEXT,
        temperatura_final_enfriamiento REAL,
        nro_termometro TEXT,
        responsable_elaboracion TEXT,
        sabor TEXT,
        olor TEXT,
        color TEXT,
        textura TEXT,
        responsable_sensorial TEXT,
        observacion TEXT
    )
''')
conn.commit()

# Sidebar para navegación
menu = ["Ingresar Muestra", "Inventario"]
eleccion = st.sidebar.selectbox("Menú", menu)

if eleccion == "Ingresar Muestra":
    st.header("Ingreso de Nueva Muestra")

    with st.form("form_muestra"):
        st.subheader("Datos Generales")
        col1, col2 = st.columns(2)
        with col1:
            fecha_elaboracion = st.date_input("Fecha Elaboración")
            producto = st.text_input("Producto")
            numero_orden = st.text_input("Número Orden de Fabricación")
        with col2:
            cantidad_muestra = st.number_input("Cantidad Muestra (g)", min_value=0.0)
            fecha_descarte = st.date_input("Fecha de Descarte/Vencimiento")
            cantidad_producto = st.number_input("Cantidad Producto (Kg-L)", min_value=0.0)

        st.subheader("Cocción y Enfriamiento")
        col3, col4 = st.columns(2)
        with col3:
            temperatura_coccion = st.number_input("Temp. Final de Cocción (°C)")
            hora_inicial_enfriamiento = st.time_input("Hora Inicial Enfriamiento")
            hora_final_enfriamiento = st.time_input("Hora Final Enfriamiento")
        with col4:
            tiempo_total_enfriamiento = st.text_input("Tiempo Total Enfriamiento")
            temperatura_final_enfriamiento = st.number_input("Temp. Enfriamiento Final (°C)")
            nro_termometro = st.text_input("Nro. Termómetro")

        responsable_elaboracion = st.text_input("Responsable Elaboración")

        st.subheader("Evaluación Sensorial")
        col5, col6 = st.columns(2)
        with col5:
            sabor = st.selectbox("Sabor", ["Bueno", "Regular", "Malo", "NC", "N/A"])
            olor = st.selectbox("Olor", ["Bueno", "Regular", "Malo", "NC", "N/A"])
        with col6:
            color = st.selectbox("Color", ["Bueno", "Regular", "Malo", "NC", "N/A"])
            textura = st.selectbox("Textura", ["Bueno", "Regular", "Malo", "NC", "N/A"])

        responsable_sensorial = st.text_input("Responsable Sensorial")
        observacion = st.text_area("Observación")

        submit_button = st.form_submit_button(label="Guardar Muestra")

        if submit_button:
            c.execute('''
                INSERT INTO muestras (
                    fecha_elaboracion, producto, numero_orden, cantidad_muestra, fecha_descarte,
                    cantidad_producto, temperatura_coccion, hora_inicial_enfriamiento,
                    hora_final_enfriamiento, tiempo_total_enfriamiento, temperatura_final_enfriamiento,
                    nro_termometro, responsable_elaboracion, sabor, olor, color, textura,
                    responsable_sensorial, observacion
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                fecha_elaboracion, producto, numero_orden, cantidad_muestra, fecha_descarte,
                cantidad_producto, temperatura_coccion, str(hora_inicial_enfriamiento),
                str(hora_final_enfriamiento), tiempo_total_enfriamiento, temperatura_final_enfriamiento,
                nro_termometro, responsable_elaboracion, sabor, olor, color, textura,
                responsable_sensorial, observacion
            ))
            conn.commit()
            st.success("Muestra guardada exitosamente!")

elif eleccion == "Inventario":
    st.header("Inventario de Muestras")

    # Cargar datos
    df = pd.read_sql_query("SELECT * FROM muestras", conn)

    if not df.empty:
        # Convertir fechas para comparación
        df['fecha_descarte'] = pd.to_datetime(df['fecha_descarte']).dt.date
        hoy = date.today()

        # Añadir columna de estado
        df['estado'] = df['fecha_descarte'].apply(
            lambda x: 'Vencido' if pd.notnull(x) and x < hoy else ('Vence Hoy' if pd.notnull(x) and x == hoy else 'Vigente')
        )

        # Mostrar notificaciones de vencimiento
        vencidos = df[df['estado'] == 'Vencido']
        if not vencidos.empty:
            st.error(f"⚠️ Alerta: Hay {len(vencidos)} muestras vencidas!")
            with st.expander("Ver muestras vencidas"):
                st.dataframe(vencidos[['producto', 'numero_orden', 'fecha_descarte']])

        # Mostrar tabla completa
        st.subheader("Todas las muestras")

        # Aplicar colores según el estado
        def color_estado(val):
            color = 'red' if val == 'Vencido' else ('orange' if val == 'Vence Hoy' else 'green')
            return f'color: {color}'

        st.dataframe(df.style.map(color_estado, subset=['estado']))
    else:
        st.info("No hay muestras registradas en el inventario.")
