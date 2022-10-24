from __future__ import annotations
from Utils import logger
import pandas as pd
import datetime as dt

def limpieza_base_de_datos(db : pd.DataFrame) -> pd.DataFrame:
    
    nan = db[db.isna().any(axis = 1)]
    db.dropna(inplace = True)
    logger(f'Se eliminaron {len(nan)} filas con datos vacíos/nulos')
    
    columnas = ['Día', 'Mes', 'Año']
    db = db.astype({ "Día": int, "Mes": int, "Año": int })
    logger('Se cambiaron los tipos de las columnas día, mes y año de flotantes a enteros')
    # Armamos una columna de fecha con las columnas de día mes y año
    db['Fecha'] = db[columnas].apply(lambda x: '-'.join(x.values.astype(str)), axis='columns')
    
    db['Fecha'] = pd.to_datetime(db['Fecha'], infer_datetime_format=True)
    logger('Se creó la columna Fecha de tipo datetime para facilitar las operaciones')
    
    
    # Chequeamos que los datos no sobrepasen las fechas dadas
    cond_false = (db['Fecha'] < dt.datetime(2005, 1, 1)) & (db['Fecha'] > dt.datetime(2022, 9, 25))
    cond_true = (db['Fecha'] >= dt.datetime(2005, 1, 1)) & (db['Fecha'] <= dt.datetime(2022, 9, 25))
    fechas_fuera = db.loc[cond_false]
    if len(fechas_fuera):
        logger('Se encontraron datos fuera del rango de fechas permitidas. Se han eliminado.')
        db = db.loc[cond_true]
    else:
        logger('No se han encontrado datos fuera del rango de fechas permitidas.')
        
    # Eliminamos las columnas Día, Mes y Año
    elim = ['Día', 'Mes', 'Año']
    logger(f'Se eliminaron las columnas {elim}')
    db.drop(columns = elim, inplace = True)
        
    return db

if __name__ == '__main__':
    # Inicializamos el archivo de logs vacío en cada ejecución
    open('logs.log', 'w')
    db = pd.read_csv('wfp_food_prices_arg_original.csv')
    
    db = limpieza_base_de_datos(db)
    
    lista_ocurrencia = db['Grupo alimenticio'].value_counts()
    logger(f'Frecuencias de Grupo alimenticio: \n{(lista_ocurrencia)}')
    logger(f'Media de las frecuencias de grupo alimenticio: {lista_ocurrencia.mean()}')
    
    # Lista de grupos mayoritarios
    list_mayoritario = lista_ocurrencia[:3].index.tolist()
    list_minoritario = lista_ocurrencia[3:].index.tolist()
    
    # Dividimos el dataframe en grupos mayoritarios y minoritarios
    frame_mayoritario = db.loc[db['Grupo alimenticio'].isin(list_mayoritario)]
    frame_minoritario = db.loc[db['Grupo alimenticio'].isin(list_minoritario)]
    
    # Media de cada columna del frame mayoritario y minoritario.
    mean_mayoritario = frame_mayoritario.mean(numeric_only = True)
    mean_minoritario = frame_minoritario.mean(numeric_only = True)
    logger(f'La media de cada columna del grupo mayoritario es de: \n{mean_mayoritario}')
    logger(f'La media de cada columna del grupo minoritario es de: \n{mean_minoritario}')
    
    # Mediana de cada columna del frame mayoritario y minoritario.
    median_mayoritario = frame_mayoritario.median(numeric_only = True)
    median_minoritario = frame_minoritario.median(numeric_only = True)
    logger(f'La mediana de cada columna del grupo mayoritario es de: \n{median_mayoritario}')
    logger(f'La mediana de cada columna del grupo minoritario es de: \n{median_minoritario}')
    
    # Mediana de cada columna del frame mayoritario y minoritario.
    mode_mayoritario = frame_mayoritario.mode(numeric_only = True)
    mode_minoritario = frame_minoritario.mode(numeric_only = True)
    logger(f'La moda de cada columna del grupo mayoritario es de: \n{mode_mayoritario}')
    logger(f'La moda de cada columna del grupo minoritario es de: \n{mode_minoritario}')
    
    # Cuartiles de cada columna del frame mayoritario y minoritario.
    cuartiles_mayoritario = frame_mayoritario.quantile(q = [.25, .5, .75], numeric_only = True)
    cuartiles_minoritario = frame_minoritario.quantile(q = [.25, .5, .75], numeric_only = True)
    logger(f'Los cuartiles de cada columna del grupo mayoritario es de: \n{cuartiles_mayoritario}')
    logger(f'Los cuartiles de cada columna del grupo minoritario es de: \n{cuartiles_minoritario}')