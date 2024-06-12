import pandas as pd
import joblib
from datetime import datetime, timedelta
import os

# Crear la carpeta 'predicciones' si no existe
predicciones_path = os.path.join(os.getcwd(), 'predicciones')
if not os.path.exists(predicciones_path):
    os.makedirs(predicciones_path)

# Determinar la última fecha en los datos originales
last_date = pd.to_datetime('2023-06-10')  # Cambiar esta fecha a la última fecha de tu conjunto de datos

# Generar predicciones para cada estación
stations = [file.split('_')[0] for file in os.listdir('models') if file.endswith('_tmax.pkl')]
for station in stations:
    # Cargar los modelos
    models = {
        'TMAX': joblib.load(f'models/{station}_tmax.pkl'),
        'TMIN': joblib.load(f'models/{station}_tmin.pkl'),
        'PRCP': joblib.load(f'models/{station}_prcp.pkl'),
        'SNWD': joblib.load(f'models/{station}_snwd.pkl')
    }

    # Crear un DataFrame para almacenar las predicciones
    future_dates = pd.date_range(start=last_date + timedelta(days=1), periods=30, freq='D')
    predictions = pd.DataFrame(index=future_dates)

    # Hacer predicciones
    for var, model in models.items():
        pred = model.get_forecast(steps=30).predicted_mean
        predictions[var] = pred.values

    # Convertir temperaturas a grados centígrados si están en Fahrenheit
    predictions['TMAX'] = (predictions['TMAX'] - 32) * 5.0/9.0
    predictions['TMIN'] = (predictions['TMIN'] - 32) * 5.0/9.0

    # Añadir columnas de día de la semana, número de día, mes y año
    predictions['Day of Week'] = predictions.index.day_name()
    predictions['Day'] = predictions.index.day
    predictions['Month'] = predictions.index.month
    predictions['Year'] = predictions.index.year

    # Guardar las predicciones en un archivo CSV para usarlas en la aplicación de Streamlit
    predictions.to_csv(f'{predicciones_path}/{station}.csv')

print("Predicciones generadas y guardadas exitosamente.")
