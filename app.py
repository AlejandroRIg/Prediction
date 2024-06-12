import folium
import streamlit as st
from streamlit_folium import folium_static
import pandas as pd
import numpy as np
import datetime
import os

# Cargar el CSV con datos de estaciones y coordenadas
file_path = '3707499.csv'
weather_data = pd.read_csv(file_path)

# Filtrar estaciones cuyo nombre comienza con 'A'
stations_data = weather_data[weather_data['NAME'].str.startswith('A')]

# Crear un diccionario con estaciones y sus coordenadas
estaciones = {
    row['NAME']: [row['LATITUDE'], row['LONGITUDE']] for _, row in stations_data.iterrows()
}

# Función para actualizar los marcadores en el mapa
def actualizar_mapa(estacion_seleccionada):
    mapa = folium.Map(location=[40.4168, -3.7038], zoom_start=6)
    for estacion, coords in estaciones.items():
        if estacion == estacion_seleccionada:
            folium.Marker(location=coords, popup=estacion, icon=folium.Icon(color='red')).add_to(mapa)
        else:
            folium.Marker(location=coords, popup=estacion).add_to(mapa)
    folium_static(mapa)

# Mostrar el mapa y el selector de estación en Streamlit
st.title("Mapa de Estaciones Meteorológicas en España")
st.write("Selecciona una estación haciendo clic en el marcador.")

# Selector de estación basado en los nombres
estacion_seleccionada = st.selectbox("Estaciones:", list(estaciones.keys()))
actualizar_mapa(estacion_seleccionada)

# Opciones para ver el pronóstico
opcion = st.radio("Mostrar prediccion sobre:", ["Próximos 7 días"])

# Cargar las predicciones
predicciones_path = os.path.join(os.getcwd(), 'predicciones')
predicciones = pd.read_csv(f'{predicciones_path}/{estacion_seleccionada}.csv', index_col=0, parse_dates=True)

# Traducir los días de la semana al español
dias_semana = {
    'Monday': 'Lunes',
    'Tuesday': 'Martes',
    'Wednesday': 'Miércoles',
    'Thursday': 'Jueves',
    'Friday': 'Viernes',
    'Saturday': 'Sábado',
    'Sunday': 'Domingo'
}

predicciones['Day of Week'] = predicciones['Day of Week'].map(dias_semana)
predicciones['Date'] = predicciones.index.strftime('%d/%m/%Y')

# Formatear las temperaturas a dos decimales y añadir el símbolo de grados
predicciones['TMAX'] = predicciones['TMAX'].apply(lambda x: f"{x:.2f}°")
predicciones['TMIN'] = predicciones['TMIN'].apply(lambda x: f"{x:.2f}°")

# Añadir columna de iconos de clima
def obtener_icono(tmax):
    if tmax > 30:
        return "🌞"
    elif tmax > 20:
        return "☀️"
    elif tmax > 10:
        return "⛅"
    else:
        return "❄️"

predicciones['Clima'] = predicciones['TMAX'].apply(lambda x: obtener_icono(float(x[:-1])))

# Ajustar el orden de las columnas
predicciones = predicciones[['Date', 'Day of Week', 'TMAX', 'TMIN', 'PRCP', 'SNWD', 'Clima']]

if opcion == "Próximos 7 días":
    st.write(f"Pronóstico del tiempo para los próximos 7 días en {estacion_seleccionada}:")
    st.table(predicciones.head(7))
else:
    fecha_seleccionada = st.date_input("Seleccione una fecha dentro del próximo mes:", min_value=predicciones.index[0], max_value=predicciones.index[-1])
    if fecha_seleccionada:
        prediccion_dia = predicciones[predicciones.index == fecha_seleccionada]
        if not prediccion_dia.empty:
            st.write(f"Pronóstico del tiempo para {fecha_seleccionada.strftime('%d/%m/%Y')} en {estacion_seleccionada}:")
            st.table(prediccion_dia)
        else:
            st.write(f"No hay datos de predicción para {fecha_seleccionada.strftime('%d/%m/%Y')}.")
