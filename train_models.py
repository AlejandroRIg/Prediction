import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
import joblib
import os

# Cargar los datos
file_path = '3707499.csv'
weather = pd.read_csv(file_path)

# Filtrar las estaciones cuyo NAME comienza con 'A'
filtered_data = weather[weather['NAME'].str.startswith('A')]

# Seleccionar las columnas relevantes
columns_to_use = ['NAME', 'LATITUDE', 'LONGITUDE', 'DATE', 'PRCP', 'SNWD', 'TMAX', 'TMIN']
filtered_data = filtered_data[columns_to_use]

# Imputar valores faltantes en las columnas relevantes
filtered_data = filtered_data.fillna(method='ffill').fillna(method='bfill')
filtered_data['DATE'] = pd.to_datetime(filtered_data['DATE'])
filtered_data.set_index('DATE', inplace=True)

# Crear una carpeta para guardar los modelos
if not os.path.exists('models'):
    os.makedirs('models')

# Probar diferentes órdenes de ARIMA
orders = [(5, 1, 0), (1, 1, 1), (2, 1, 2)]

# Función para entrenar y guardar modelos ARIMA
def train_and_save_model(series, orders, model_name):
    best_model = None
    best_aic = float('inf')
    for order in orders:
        try:
            model = ARIMA(series, order=order)
            model_fit = model.fit()
            if model_fit.aic < best_aic:
                best_aic = model_fit.aic
                best_model = model_fit
        except Exception as e:
            print(f"Error with order {order}: {e}")
            continue
    joblib.dump(best_model, f'models/{model_name}.pkl')
    return best_model

# Entrenar y guardar modelos para cada estación
stations = filtered_data['NAME'].unique()
for station in stations:
    station_data = filtered_data[filtered_data['NAME'] == station]
    train_and_save_model(station_data['TMAX'], orders, f'{station}_tmax')
    train_and_save_model(station_data['TMIN'], orders, f'{station}_tmin')
    train_and_save_model(station_data['PRCP'], orders, f'{station}_prcp')
    train_and_save_model(station_data['SNWD'], orders, f'{station}_snwd')

print("Modelos entrenados y guardados exitosamente.")
